import { Navigate, Outlet } from "react-router-dom";

import { useAuthStore } from "@/stores/auth-store";

export function GuestRoute() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return <Outlet />;
}
