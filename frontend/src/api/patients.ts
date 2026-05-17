import { apiClient } from "@/api/client";
import type { PaginatedResponse, Patient } from "@/types/api";

export const patientsApi = {
  list: (params?: Record<string, string>) =>
    apiClient.get<PaginatedResponse<Patient>>("/patients/", { params }),
  riskSorted: () => apiClient.get<PaginatedResponse<Patient>>("/patients/risk-sorted/"),
  get: (id: string) => apiClient.get<Patient>(`/patients/${id}/`),
  me: () => apiClient.get<Patient>("/patients/me/"),
};
