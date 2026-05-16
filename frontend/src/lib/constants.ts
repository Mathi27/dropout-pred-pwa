export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";

export const ROLES = {
  PATIENT: "patient",
  DOCTOR: "doctor",
  RECEPTIONIST: "receptionist",
  ADMIN: "admin",
} as const;

export type UserRole = (typeof ROLES)[keyof typeof ROLES];

export const ROLE_LABELS: Record<UserRole, string> = {
  patient: "Patient",
  doctor: "Doctor",
  receptionist: "Receptionist",
  admin: "Admin",
};
