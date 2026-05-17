import { apiClient } from "@/api/client";
import type {
  AuditLog,
  ClinicalNote,
  PaginatedResponse,
  PatientTreatment,
  Payment,
} from "@/types/api";

export const treatmentsApi = {
  list: () => apiClient.get<PaginatedResponse<{ id: string; name: string }>>("/treatments/"),
};

export const patientTreatmentsApi = {
  list: (params?: Record<string, string>) =>
    apiClient.get<PaginatedResponse<PatientTreatment>>("/patient-treatments/", { params }),
};

export const paymentsApi = {
  list: (params?: Record<string, string>) =>
    apiClient.get<PaginatedResponse<Payment>>("/payments/", { params }),
};

export const clinicalNotesApi = {
  list: (params?: Record<string, string>) =>
    apiClient.get<PaginatedResponse<ClinicalNote>>("/clinical-notes/", { params }),
  create: (data: { patient_id: string; content: string; visit_date: string }) =>
    apiClient.post<ClinicalNote>("/clinical-notes/", data),
};

export const auditLogsApi = {
  list: (params?: Record<string, string>) =>
    apiClient.get<PaginatedResponse<AuditLog>>("/audit-logs/", { params }),
};

export const usersApi = {
  list: (params?: Record<string, string>) =>
    apiClient.get<PaginatedResponse<{ id: string; email: string; role: string; full_name: string; is_active: boolean }>>(
      "/users/",
      { params },
    ),
};
