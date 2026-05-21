from apps.ai_predictions.models import ModelVersion


def get_active_model_metrics():
    model_version = ModelVersion.objects.filter(is_active=True).order_by("-trained_at").first()
    if not model_version:
        return None
    return model_version, {
        "metrics": model_version.metrics or {},
        "calibration": model_version.calibration or {},
    }
