from django.urls import path

from apps.ai_predictions.views import (
    AnalyticsOverviewView,
    AutomationStatusView,
    HighRiskPatientsView,
    ModelMetricsView,
    PatientRiskView,
    PredictionGenerateView,
    PredictionHistoryView,
    PatientRiskTimelineView,
    PatientJourneyView,
    PredictAllPatientsView,
    RiskTrendsView,
    ShapExplanationView,
)

urlpatterns = [
    path("ai/predictions/", PredictionGenerateView.as_view(), name="ai-prediction-generate"),
    path("ai/predictions/risk/", PatientRiskView.as_view(), name="ai-patient-risk"),
    path("ai/predictions/shap/", ShapExplanationView.as_view(), name="ai-shap"),
    path("ai/predictions/high-risk/", HighRiskPatientsView.as_view(), name="ai-high-risk"),
    path("ai/predictions/history/", PredictionHistoryView.as_view(), name="ai-history"),
    path("ai/predictions/timeline/", PatientRiskTimelineView.as_view(), name="ai-timeline"),
    path("ai/predictions/journey/", PatientJourneyView.as_view(), name="ai-journey"),
    path("ai/workflows/predict-all/", PredictAllPatientsView.as_view(), name="ai-predict-all"),
    path("ai/workflows/status/", AutomationStatusView.as_view(), name="ai-workflow-status"),
    path("ai/models/metrics/", ModelMetricsView.as_view(), name="ai-model-metrics"),
    path("ai/analytics/risk-trends/", RiskTrendsView.as_view(), name="ai-risk-trends"),
    path("ai/analytics/overview/", AnalyticsOverviewView.as_view(), name="ai-analytics-overview"),
]
