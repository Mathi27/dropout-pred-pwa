import time
from functools import lru_cache

import joblib
import pandas as pd

from apps.ai_predictions.models import AIPrediction, ModelVersion, PredictionLog, PredictionStatus
from apps.ai_predictions.services.features import FEATURE_NAMES, build_patient_features
from apps.ai_predictions.services.risk import classify_risk
from apps.core.services import create_audit_log


def get_active_model_version():
    return ModelVersion.objects.filter(is_active=True).order_by("-trained_at").first()


@lru_cache(maxsize=4)
def _load_model_cached(model_path: str):
    return joblib.load(model_path)


def load_model(model_version: ModelVersion):
    return _load_model_cached(model_version.model_path)


def get_latest_prediction(patient):
    return AIPrediction.objects.filter(patient=patient).order_by("-created_at").first()


def get_latest_risk_score(patient):
    prediction = get_latest_prediction(patient)
    if not prediction:
        return None
    return round(prediction.probability * 100, 1)


def generate_prediction(*, patient, user=None, source="api") -> AIPrediction:
    start = time.monotonic()
    model_version = get_active_model_version()
    if not model_version:
        raise ValueError("No active model available.")

    features = build_patient_features(patient)
    feature_names = model_version.feature_names or FEATURE_NAMES

    try:
        model = load_model(model_version)
        frame = pd.DataFrame([features]).reindex(columns=feature_names).fillna(0)
        probability = float(model.predict_proba(frame)[:, 1][0])
        risk_level = classify_risk(probability)
        prediction = AIPrediction.objects.create(
            patient=patient,
            model_version=model_version,
            probability=probability,
            risk_level=risk_level,
            features=features,
            prediction_source=source,
        )
        # create an audit log so the realtime pipeline can broadcast this prediction
        try:
            create_audit_log(
                actor=user,
                action="ai_prediction.created",
                resource_type="ai_prediction",
                resource_id=str(prediction.id),
            )
        except Exception:
            pass
        latency_ms = int((time.monotonic() - start) * 1000)
        PredictionLog.objects.create(
            patient=patient,
            model_version=model_version,
            prediction=prediction,
            status=PredictionStatus.SUCCESS,
            latency_ms=latency_ms,
            metadata={"actor": str(getattr(user, "id", ""))},
            source=source,
        )
        return prediction
    except Exception as exc:
        latency_ms = int((time.monotonic() - start) * 1000)
        PredictionLog.objects.create(
            patient=patient,
            model_version=model_version,
            status=PredictionStatus.FAILED,
            latency_ms=latency_ms,
            error_message=str(exc),
            metadata={"actor": str(getattr(user, "id", ""))},
            source=source,
        )
        raise
