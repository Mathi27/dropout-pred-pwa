import numpy as np
import pandas as pd
import shap

from apps.ai_predictions.models import ModelType, ShapExplanation
from apps.core.services import create_audit_log
from apps.ai_predictions.services.features import FEATURE_NAMES, build_patient_features
from apps.ai_predictions.services.predictor import load_model


def get_or_create_explanation(prediction):
    existing = ShapExplanation.objects.filter(prediction=prediction).first()
    if existing:
        return existing

    model_version = prediction.model_version
    if model_version.model_type not in (ModelType.RANDOM_FOREST, ModelType.XGBOOST):
        raise ValueError("SHAP TreeExplainer requires a tree-based model.")

    model = load_model(model_version)
    features = prediction.features or build_patient_features(prediction.patient)
    feature_names = model_version.feature_names or FEATURE_NAMES
    frame = pd.DataFrame([features]).reindex(columns=feature_names).fillna(0)

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(frame)
    if isinstance(shap_values, list):
        shap_values = shap_values[1]
    shap_row = np.array(shap_values)[0]

    base_value = explainer.expected_value
    if isinstance(base_value, (list, tuple, np.ndarray)):
        base_value = float(np.array(base_value).flatten()[-1])
    else:
        base_value = float(base_value)

    shap_map = {name: float(val) for name, val in zip(feature_names, shap_row)}
    top_features = sorted(
        (
            {
                "feature": name,
                "value": float(value),
                "impact": abs(float(value)),
            }
            for name, value in shap_map.items()
        ),
        key=lambda item: item["impact"],
        reverse=True,
    )[:6]

    explanation = ShapExplanation.objects.create(
        prediction=prediction,
        patient=prediction.patient,
        model_version=model_version,
        base_value=base_value,
        shap_values=shap_map,
        top_features=top_features,
        feature_values=features,
    )
    try:
        create_audit_log(
            actor=None,
            action="shap_explanation.created",
            resource_type="shap_explanation",
            resource_id=str(explanation.id),
            metadata={"prediction_id": str(prediction.id), "patient_id": str(prediction.patient.id)},
        )
    except Exception:
        pass
    return explanation
