import type { UserRole } from "@/lib/constants";

export interface User {
  id: string;
  email: string;
  phone: string;
  first_name: string;
  last_name: string;
  full_name: string;
  role: UserRole;
  clinic_id: string | null;
  preferred_language: string;
  email_verified: boolean;
  phone_verified: boolean;
  is_active: boolean;
  created_at: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface LoginResponse {
  access: string;
  refresh: string;
  user: User;
}

export interface RegisterPayload {
  email: string;
  password: string;
  password_confirm: string;
  first_name?: string;
  last_name?: string;
  phone?: string;
  role?: UserRole;
  preferred_language?: string;
}

export interface RegisterResponse {
  user: User;
  tokens: AuthTokens;
}
