from celery import shared_task

from apps.ai_predictions.services.monitoring import monitor_risk_thresholds
from apps.ai_predictions.services.workflows import predict_all_patients
from apps.ai_predictions.services.analytics import refresh_ai_analytics_cache
from apps.core.analytics import refresh_admin_analytics_cache
from apps.ai_interventions.services.automation import queue_interventions_for_high_risk


@shared_task
def predict_all_patients_task():
    return predict_all_patients(source="scheduled")


@shared_task
def refresh_analytics_task():
    admin = refresh_admin_analytics_cache()
    ai = refresh_ai_analytics_cache()
    return {"admin": admin, "ai": ai}


@shared_task
def monitor_risk_thresholds_task():
    return monitor_risk_thresholds()


@shared_task
def daily_prediction_simulation_task():
    predictions = predict_all_patients(source="scheduled")
    queue = queue_interventions_for_high_risk(source="scheduled")
    monitoring = monitor_risk_thresholds()
    refresh_admin_analytics_cache()
    refresh_ai_analytics_cache()
    return {
        "predictions": predictions,
        "queue": queue,
        "monitoring": monitoring,
    }
