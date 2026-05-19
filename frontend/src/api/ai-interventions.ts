import { apiClient } from "@/api/client";
import type {
  AIGeneratedMessage,
  InterventionLog,
  InterventionMetrics,
} from "@/types/api";

export const aiInterventionsApi = {
  preview: (payload: { patient_id: string; message_type?: string; language?: string }) =>
    apiClient.post<AIGeneratedMessage>("/ai/interventions/preview/", payload),
  generate: (payload: { patient_id: string; message_type?: string; language?: string; channel?: string }) =>
    apiClient.post<AIGeneratedMessage>("/ai/interventions/generate/", payload),
  patientHistory: (patientId: string, limit = 30) =>
    apiClient.get<AIGeneratedMessage[]>("/ai/interventions/patient/", {
      params: { patient_id: patientId, limit },
    }),
  interventionHistory: (patientId?: string) =>
    apiClient.get<InterventionLog[]>("/ai/interventions/history/", {
      params: patientId ? { patient_id: patientId } : {},
    }),
  metrics: () => apiClient.get<InterventionMetrics>("/ai/interventions/metrics/"),
  simulateDelivery: (messageId: string) =>
    apiClient.post<{ delivery: string; message_id: string }>("/ai/interventions/delivery/simulate/", {
      message_id: messageId,
    }),
  retryDelivery: (messageId: string) =>
    apiClient.post<{ delivery: string; message_id: string }>("/ai/interventions/delivery/retry/", {
      message_id: messageId,
    }),
};
