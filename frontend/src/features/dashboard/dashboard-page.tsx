import { Activity, Calendar, TrendingUp, Users } from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { ROLE_LABELS } from "@/lib/constants";
import { useAuthStore } from "@/stores/auth-store";

const ROLE_PLACEHOLDERS: Record<string, { title: string; description: string }> = {
  patient: {
    title: "Your treatment journey",
    description: "Track appointments, progress, and personalized reminders.",
  },
  doctor: {
    title: "Patient risk overview",
    description: "View patients sorted by dropout risk — full AI panel in Phase 4.",
  },
  receptionist: {
    title: "Today's schedule",
    description: "Manage appointments and attendance — coming in Phase 3.",
  },
  admin: {
    title: "Clinic KPIs",
    description: "Monitor dropout rates, model performance, and clinic analytics.",
  },
};

export function DashboardPage() {
  const user = useAuthStore((s) => s.user);
  const placeholder = user ? ROLE_PLACEHOLDERS[user.role] : null;

  const stats = [
    { label: "Active patients", value: "—", icon: Users },
    { label: "Appointments today", value: "—", icon: Calendar },
    { label: "Completion rate", value: "—", icon: TrendingUp },
    { label: "High-risk alerts", value: "—", icon: Activity },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">
          {placeholder?.title ?? "Dashboard"}
        </h1>
        <p className="text-muted-foreground">
          {user && (
            <span className="mr-2 rounded-full bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary">
              {ROLE_LABELS[user.role]}
            </span>
          )}
          {placeholder?.description ?? "Loading your workspace…"}
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.label}>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {stat.label}
              </CardTitle>
              <stat.icon className="h-4 w-4 text-primary" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Phase 1 workspace</CardTitle>
          <CardDescription>
            Authentication, RBAC, and dashboard shell are ready. AI predictions and full modules
            ship in later phases per the INAHS 2026 blueprint.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-4/5" />
          <Skeleton className="h-4 w-3/5" />
        </CardContent>
      </Card>
    </div>
  );
}
