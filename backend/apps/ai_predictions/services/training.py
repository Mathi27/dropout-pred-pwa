from __future__ import annotations

from pathlib import Path
import hashlib
import math

import joblib
import numpy as np
import pandas as pd
from django.conf import settings
from django.utils import timezone
from sklearn.calibration import calibration_curve
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    brier_score_loss,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

from apps.ai_predictions.models import ModelType, ModelVersion
from apps.ai_predictions.services.features import FEATURE_NAMES, build_patient_features
from apps.patients.models import Patient
from apps.patient_treatments.models import PatientTreatment, TreatmentStatus

MODEL_DIR = Path(settings.BASE_DIR) / "ml_models" / "ai_predictions"


def _derive_dropout_label(patient, features: dict) -> int:
    cancelled = PatientTreatment.objects.filter(
        patient=patient,
        status__in=[TreatmentStatus.CANCELLED, TreatmentStatus.ON_HOLD],
    ).exists()
    score = (
        features["visit_miss_rate"] * 2.5
        + min(features["consecutive_misses"] / 3, 1) * 1.8
        + min(features["days_since_last_visit"] / 90, 1) * 1.2
        + (1 - min(features["treatment_completion_pct"] / 100, 1)) * 1.6
        + min(features["overdue_payment_days"] / 60, 1) * 1.1
        + (1 - min(features["notification_response_rate"], 1)) * 1.0
        + min(features["avg_appointment_gap"] / 30, 1) * 0.8
        + (0.9 if cancelled else 0)
    )
    probability = 1 / (1 + math.exp(-(score - 4.2)))
    probability = min(max(probability, 0.05), 0.9)
    digest = hashlib.md5(str(patient.id).encode()).hexdigest()
    roll = int(digest[:8], 16) / 0xFFFFFFFF
    return 1 if roll < probability else 0


def build_training_dataset(patients=None):
    patients = patients or Patient.objects.select_related("user")
    rows = []
    labels = []
    for patient in patients:
        features = build_patient_features(patient)
        rows.append(features)
        labels.append(_derive_dropout_label(patient, features))
    frame = pd.DataFrame(rows).reindex(columns=FEATURE_NAMES).fillna(0)
    labels_array = np.array(labels)
    label_strategy = "weighted_prob"
    if len(labels_array) >= 2 and len(np.unique(labels_array)) < 2:
        scores = (
            frame["visit_miss_rate"].clip(0, 1) * 2.0
            + frame["consecutive_misses"].clip(0, 5) / 5.0
            + frame["days_since_last_visit"].clip(0, 120) / 120.0
            + (1 - frame["treatment_completion_pct"].clip(0, 100) / 100.0)
            + frame["overdue_payment_days"].clip(0, 90) / 90.0
            + (1 - frame["notification_response_rate"].clip(0, 1))
            + frame["avg_appointment_gap"].clip(0, 45) / 45.0
        )
        order = np.argsort(scores.to_numpy())
        positives = max(1, int(len(scores) * 0.3))
        labels_array = np.zeros(len(scores), dtype=int)
        labels_array[order[-positives:]] = 1
        label_strategy = "fallback_rank"
    summary = {
        "patients": int(len(labels)),
        "positive_rate": float(labels_array.mean()) if len(labels_array) else 0.0,
        "label_strategy": label_strategy,
    }
    return frame, labels_array, summary


def _evaluate_model(model, x_test, y_test):
    proba = model.predict_proba(x_test)[:, 1]
    preds = (proba >= 0.5).astype(int)
    metrics = {
        "auc": float(roc_auc_score(y_test, proba)),
        "f1": float(f1_score(y_test, preds, zero_division=0)),
        "precision": float(precision_score(y_test, preds, zero_division=0)),
        "recall": float(recall_score(y_test, preds, zero_division=0)),
        "brier": float(brier_score_loss(y_test, proba)),
    }
    frac_pos, mean_pred = calibration_curve(y_test, proba, n_bins=6)
    calibration = {
        "curve": [
            {"mean_pred": float(m), "fraction_pos": float(f)}
            for m, f in zip(mean_pred, frac_pos)
        ]
    }
    return metrics, calibration


def _save_model(model, model_type: str) -> str:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
    path = MODEL_DIR / f"{model_type}_{timestamp}.joblib"
    joblib.dump(model, path)
    return str(path)


def _safe_params(model) -> dict:
    params = model.get_params() if hasattr(model, "get_params") else {}
    def _sanitize_value(value):
        if isinstance(value, dict):
            return {k: _sanitize_value(v) for k, v in value.items()}
        if isinstance(value, (list, tuple)):
            return [_sanitize_value(v) for v in value]
        if isinstance(value, (np.integer,)):
            return int(value)
        if isinstance(value, (np.floating, float)):
            numeric = float(value)
            if not math.isfinite(numeric):
                return None
            return numeric
        if isinstance(value, (str, int, bool)) or value is None:
            return value
        return str(value)

    return {key: _sanitize_value(value) for key, value in params.items()}


def train_models(*, set_active: bool = True):
    x, y, summary = build_training_dataset()
    if len(np.unique(y)) < 2:
        raise ValueError("Insufficient class variation to train models.")

    class_counts = np.bincount(y)
    min_class = int(class_counts.min()) if len(class_counts) else 0
    if min_class < 2:
        raise ValueError("Not enough samples per class to train models.")

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    models = {
        ModelType.LOGISTIC_REGRESSION: Pipeline(
            [
                ("scaler", StandardScaler()),
                ("model", LogisticRegression(max_iter=1000, class_weight="balanced")),
            ]
        ),
        ModelType.RANDOM_FOREST: RandomForestClassifier(
            n_estimators=200,
            max_depth=6,
            class_weight="balanced",
            random_state=42,
        ),
        ModelType.XGBOOST: XGBClassifier(
            n_estimators=250,
            max_depth=4,
            learning_rate=0.08,
            subsample=0.9,
            colsample_bytree=0.9,
            eval_metric="logloss",
            random_state=42,
        ),
    }

    created_versions = []
    for model_type, model in models.items():
        model.fit(x_train, y_train)
        metrics, calibration = _evaluate_model(model, x_test, y_test)

        n_splits = min(4, min_class)
        if n_splits >= 2:
            cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
            cv_scores = cross_val_score(model, x, y, cv=cv, scoring="roc_auc")
            metrics["cv_auc_mean"] = float(cv_scores.mean())
            metrics["cv_auc_std"] = float(cv_scores.std())

        model_path = _save_model(model, model_type)
        version = ModelVersion.objects.create(
            name=f"{model_type.replace('_', ' ').title()} {timezone.now():%Y-%m-%d}",
            model_type=model_type,
            is_active=False,
            trained_at=timezone.now(),
            metrics=metrics,
            calibration=calibration,
            feature_names=FEATURE_NAMES,
            hyperparameters=_safe_params(model),
            data_summary=summary,
            model_path=model_path,
        )
        created_versions.append(version)

    if set_active and created_versions:
        best = max(created_versions, key=lambda v: v.metrics.get("auc", 0))
        ModelVersion.objects.filter(is_active=True).update(is_active=False)
        best.is_active = True
        best.save(update_fields=["is_active", "updated_at"])

    return created_versions
