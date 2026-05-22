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

export const doctorsApi = {
  list: (params?: Record<string, string>) =>
    apiClient.get<PaginatedResponse<{ id: string; full_name: string; specialization?: string; is_available?: boolean }>>(
      "/doctors/",
      { params },
    ),
};

export const patientTreatmentsApi = {
  list: (params?: Record<string, string>) =>
    apiClient.get<PaginatedResponse<PatientTreatment>>("/patient-treatments/", { params }),
  update: (id: string, data: Partial<PatientTreatment>) =>
    apiClient.patch<PatientTreatment>(`/patient-treatments/${id}/`, data),
  updateProgress: (id: string, progress_percent: number) =>
    apiClient.post<PatientTreatment>(`/patient-treatments/${id}/update-progress/`, { progress_percent }),
};

export const paymentsApi = {
  list: (params?: Record<string, string>) =>
    apiClient.get<PaginatedResponse<Payment>>("/payments/", { params }),
  create: (data: {
    patient_id: string;
    amount: number;
    payment_date: string;
    status?: string;
    method?: string;
    reference?: string;
    description?: string;
  }) => apiClient.post<Payment>("/payments/", data),
  update: (id: string, data: Partial<Payment>) =>
    apiClient.patch<Payment>(`/payments/${id}/`, data),
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
  update: (id: string, data: Partial<{ role: string; is_active: boolean }>) =>
    apiClient.patch(`/users/${id}/`, data),
};
