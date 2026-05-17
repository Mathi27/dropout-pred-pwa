import { apiClient } from "@/api/client";
import type { Appointment, PaginatedResponse } from "@/types/api";

export const appointmentsApi = {
  list: (params?: Record<string, string>) =>
    apiClient.get<PaginatedResponse<Appointment>>("/appointments/", { params }),
  get: (id: string) => apiClient.get<Appointment>(`/appointments/${id}/`),
  create: (data: Partial<Appointment> & { patient_id: string; doctor_id?: string }) =>
    apiClient.post<Appointment>("/appointments/", data),
  update: (id: string, data: Partial<Appointment>) =>
    apiClient.patch<Appointment>(`/appointments/${id}/`, data),
  markAttendance: (id: string, attendance: string) =>
    apiClient.post<Appointment>(`/appointments/${id}/mark-attendance/`, { attendance }),
  reschedule: (id: string, scheduled_at: string) =>
    apiClient.post<Appointment>(`/appointments/${id}/reschedule/`, { scheduled_at }),
};
