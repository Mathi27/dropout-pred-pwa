import { apiClient } from "@/api/client";
import type { AdminAnalytics } from "@/types/api";

export const analyticsApi = {
  admin: () => apiClient.get<AdminAnalytics>("/analytics/admin/"),
  doctor: () => apiClient.get<Record<string, number>>("/analytics/doctor/"),
};
