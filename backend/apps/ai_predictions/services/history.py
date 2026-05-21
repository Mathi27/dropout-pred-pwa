from apps.ai_predictions.models import AIPrediction


def get_prediction_history(*, patient, limit=25):
    return AIPrediction.objects.filter(patient=patient).order_by("-created_at")[:limit]
