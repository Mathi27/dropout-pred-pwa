import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import { GuestRoute } from "@/components/auth/guest-route";
import { ProtectedRoute } from "@/components/auth/protected-route";
import { AuthLayout } from "@/components/layout/auth-layout";
import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { AuditLogsPage } from "@/features/admin/audit-logs-page";
import { AdminUsersPage } from "@/features/admin/users-page";
import { RiskAnalyticsPage } from "@/features/ai/risk-analytics-page";
import { AppointmentsPage } from "@/features/appointments/appointments-page";
import { ForgotPasswordPage } from "@/features/auth/forgot-password-page";
import { LoginPage } from "@/features/auth/login-page";
import { OtpLoginPage } from "@/features/auth/otp-login-page";
import { RegisterPage } from "@/features/auth/register-page";
import { ClinicalPage } from "@/features/clinical/clinical-page";
import { DashboardPage } from "@/features/dashboard/dashboard-page";
import { NotificationsPage } from "@/features/notifications/notifications-page";
import { PatientDetailPage } from "@/features/patients/patient-detail-page";
import { PatientsPage } from "@/features/patients/patients-page";
import { RemindersPage } from "@/features/receptionist/reminders-page";
import { SchedulePage } from "@/features/receptionist/schedule-page";
import { SettingsPage } from "@/features/settings/settings-page";
import { InterventionsPage } from "@/features/interventions/interventions-page";

export function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />

        <Route element={<GuestRoute />}>
          <Route element={<AuthLayout />}>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/forgot-password" element={<ForgotPasswordPage />} />
            <Route path="/otp-login" element={<OtpLoginPage />} />
          </Route>
        </Route>

        <Route element={<ProtectedRoute />}>
          <Route element={<DashboardLayout />}>
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/appointments" element={<AppointmentsPage />} />
            <Route path="/notifications" element={<NotificationsPage />} />
            <Route path="/settings" element={<SettingsPage />} />

            <Route element={<ProtectedRoute allowedRoles={["doctor", "admin"]} />}>
              <Route path="/patients" element={<PatientsPage />} />
              <Route path="/patients/:id" element={<PatientDetailPage />} />
              <Route path="/ai-insights" element={<RiskAnalyticsPage />} />
              <Route path="/interventions" element={<InterventionsPage />} />
            </Route>

            <Route element={<ProtectedRoute allowedRoles={["doctor"]} />}>
              <Route path="/clinical" element={<ClinicalPage />} />
            </Route>

            <Route element={<ProtectedRoute allowedRoles={["receptionist", "admin"]} />}>
              <Route path="/schedule" element={<SchedulePage />} />
            </Route>

            <Route element={<ProtectedRoute allowedRoles={["receptionist"]} />}>
              <Route path="/reminders" element={<RemindersPage />} />
            </Route>

            <Route element={<ProtectedRoute allowedRoles={["admin"]} />}>
              <Route path="/admin/users" element={<AdminUsersPage />} />
              <Route path="/admin/audit" element={<AuditLogsPage />} />
            </Route>
          </Route>
        </Route>

        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
