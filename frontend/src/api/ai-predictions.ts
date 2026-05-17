import { apiClient } from "@/api/client";
import type {
  AIPrediction,
  AIAnalyticsOverview,
  ModelMetrics,
  PatientTimelineEvent,
  RiskTrendPoint,
  ShapExplanation,
} from "@/types/api";

export const aiPredictionsApi = {
  generate: (patientId?: string) =>
    apiClient.post<AIPrediction>("/ai/predictions/", patientId ? { patient_id: patientId } : {}),
  getRisk: (patientId?: string) =>
    apiClient.get<AIPrediction>("/ai/predictions/risk/", {
      params: patientId ? { patient_id: patientId } : {},
    }),
  getShap: (patientId?: string) =>
    apiClient.get<ShapExplanation>("/ai/predictions/shap/", {
      params: patientId ? { patient_id: patientId } : {},
    }),
  history: (patientId: string, limit = 25) =>
    apiClient.get<AIPrediction[]>("/ai/predictions/history/", {
      params: { patient_id: patientId, limit },
    }),
  highRisk: () => apiClient.get<AIPrediction[]>("/ai/predictions/high-risk/"),
  metrics: () => apiClient.get<ModelMetrics>("/ai/models/metrics/"),
  riskTrends: (days = 30) =>
    apiClient.get<RiskTrendPoint[]>("/ai/analytics/risk-trends/", { params: { days } }),
  overview: (days = 30) =>
    apiClient.get<AIAnalyticsOverview>("/ai/analytics/overview/", { params: { days } }),
  timeline: (patientId: string, days = 120) =>
    apiClient.get<{ events: PatientTimelineEvent[] }>("/ai/predictions/timeline/", {
      params: { patient_id: patientId, days },
    }),
};
