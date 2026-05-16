import { apiClient } from "@/api/client";
import type {
  LoginResponse,
  RegisterPayload,
  RegisterResponse,
  User,
} from "@/types/auth";

export interface LoginPayload {
  email: string;
  password: string;
}

export const authApi = {
  register: (payload: RegisterPayload) =>
    apiClient.post<RegisterResponse>("/auth/register/", payload),

  login: (payload: LoginPayload) =>
    apiClient.post<LoginResponse>("/auth/login/", payload),

  me: () => apiClient.get<User>("/auth/me/"),

  logout: (refresh: string) =>
    apiClient.post("/auth/logout/", { refresh }),

  refresh: (refresh: string) =>
    apiClient.post<{ access: string; refresh?: string }>("/auth/refresh/", {
      refresh,
    }),
};
