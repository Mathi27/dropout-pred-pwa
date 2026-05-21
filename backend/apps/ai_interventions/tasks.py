from celery import shared_task

from apps.ai_interventions.services.automation import process_delivery_retries, queue_interventions_for_high_risk


@shared_task
def queue_interventions_task():
    return queue_interventions_for_high_risk(source="scheduled")


@shared_task
def retry_failed_deliveries_task():
    return process_delivery_retries()
