import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import { GuestRoute } from "@/components/auth/guest-route";
import { ProtectedRoute } from "@/components/auth/protected-route";
import { AuthLayout } from "@/components/layout/auth-layout";
import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { LoginPage } from "@/features/auth/login-page";
import { RegisterPage } from "@/features/auth/register-page";
import { DashboardPage } from "@/features/dashboard/dashboard-page";
import { PlaceholderPage } from "@/features/shared/placeholder-page";

export function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />

        <Route element={<GuestRoute />}>
          <Route element={<AuthLayout />}>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
          </Route>
        </Route>

        <Route element={<ProtectedRoute />}>
          <Route element={<DashboardLayout />}>
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route
              path="/appointments"
              element={
                <PlaceholderPage title="Appointments" description="Book and manage visits — Phase 3." />
              }
            />
            <Route element={<ProtectedRoute allowedRoles={["doctor", "admin"]} />}>
              <Route
                path="/patients"
                element={
                  <PlaceholderPage title="Patients" description="Risk-sorted patient list — Phase 4." />
                }
              />
            </Route>
            <Route element={<ProtectedRoute allowedRoles={["receptionist", "admin"]} />}>
              <Route
                path="/schedule"
                element={
                  <PlaceholderPage title="Schedule" description="Daily appointment schedule — Phase 3." />
                }
              />
            </Route>
            <Route element={<ProtectedRoute allowedRoles={["doctor"]} />}>
              <Route
                path="/clinical"
                element={
                  <PlaceholderPage title="Clinical notes" description="Doctor notes and SHAP panel — Phase 4." />
                }
              />
            </Route>
            <Route
              path="/settings"
              element={<PlaceholderPage title="Settings" description="Profile and preferences." />}
            />
          </Route>
        </Route>

        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
