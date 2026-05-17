import { apiClient } from "@/api/client";
import type { Notification, PaginatedResponse } from "@/types/api";

export const notificationsApi = {
  list: (params?: Record<string, string>) =>
    apiClient.get<PaginatedResponse<Notification>>("/notifications/", { params }),
  unreadCount: () => apiClient.get<{ count: number }>("/notifications/unread-count/"),
  markRead: (id: string) => apiClient.post(`/notifications/${id}/mark-read/`),
  markAllRead: () => apiClient.post("/notifications/mark-all-read/"),
  create: (data: { user: string; title: string; body: string; notification_type?: string }) =>
    apiClient.post<Notification>("/notifications/", data),
};
