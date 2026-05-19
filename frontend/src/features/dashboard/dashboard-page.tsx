import { AdminDashboard } from "@/features/dashboard/admin-dashboard";
import { DoctorDashboard } from "@/features/dashboard/doctor-dashboard";
import { PatientDashboard } from "@/features/dashboard/patient-dashboard";
import { ReceptionistDashboard } from "@/features/dashboard/receptionist-dashboard";
import { useAuthStore } from "@/stores/auth-store";

export function DashboardPage() {
  const role = useAuthStore((s) => s.user?.role);

  switch (role) {
    case "patient":
      return <PatientDashboard />;
    case "doctor":
      return <DoctorDashboard />;
    case "receptionist":
      return <ReceptionistDashboard />;
    case "admin":
      return <AdminDashboard />;
    default:
      return <PatientDashboard />;
  }
}
