import { Outlet } from "react-router-dom";

export function AuthLayout() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-br from-teal-50 via-white to-slate-50 p-4 dark:from-slate-950 dark:via-background dark:to-slate-900">
      <Outlet />
      <p className="mt-8 text-center text-xs text-muted-foreground">
        DentalAI · INAHS 2026 Research · Treatment Adherence Platform
      </p>
    </div>
  );
}
