from django.urls import path

from apps.ai_interventions.views import (
    DeliveryRetryView,
    DeliverySimulateView,
    InterventionQueueView,
    InterventionHistoryView,
    InterventionMetricsView,
    MessageGenerateView,
    MessagePreviewView,
    PatientCommunicationsView,
)

urlpatterns = [
    path("ai/interventions/preview/", MessagePreviewView.as_view(), name="ai-message-preview"),
    path("ai/interventions/generate/", MessageGenerateView.as_view(), name="ai-message-generate"),
    path("ai/interventions/patient/", PatientCommunicationsView.as_view(), name="ai-message-history"),
    path("ai/interventions/history/", InterventionHistoryView.as_view(), name="ai-intervention-history"),
    path("ai/interventions/metrics/", InterventionMetricsView.as_view(), name="ai-intervention-metrics"),
    path("ai/interventions/queue/", InterventionQueueView.as_view(), name="ai-intervention-queue"),
    path("ai/interventions/delivery/simulate/", DeliverySimulateView.as_view(), name="ai-delivery-simulate"),
    path("ai/interventions/delivery/retry/", DeliveryRetryView.as_view(), name="ai-delivery-retry"),
]
