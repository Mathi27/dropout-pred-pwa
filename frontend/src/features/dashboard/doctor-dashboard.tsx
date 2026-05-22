import { useQuery } from "@tanstack/react-query";
import { useMemo } from "react";
import { Activity, Calendar, TrendingUp, Users } from "lucide-react";
import { Link } from "react-router-dom";

import { analyticsApi } from "@/api/analytics";
import { appointmentsApi } from "@/api/appointments";
import { patientsApi } from "@/api/patients";
import { AppointmentTrendChart } from "@/components/charts/appointment-trend-chart";
import { PageHeader } from "@/components/shared/page-header";
import { PageSkeleton } from "@/components/shared/page-skeleton";
import { StatCard } from "@/components/shared/stat-card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";

import { cn } from "@/lib/utils";

function riskLevel(score: number) {
  if (score > 70) return { label: "High", className: "bg-destructive/15 text-destructive ring-destructive/20" };
  if (score > 40) return { label: "Medium", className: "bg-amber-500/15 text-amber-700 ring-amber-500/20 dark:text-amber-400" };
  return { label: "Low", className: "bg-primary/15 text-primary ring-primary/20" };
}

export function DoctorDashboard() {
  const { data: analytics, isLoading } = useQuery({
    queryKey: ["doctor-analytics"],
    queryFn: () => analyticsApi.doctor().then((r) => r.data),
  });

  const { data: patients, isLoading: patientsLoading } = useQuery({
    queryKey: ["patients-risk"],
    queryFn: () => patientsApi.riskSorted().then((r) => r.data),
  });

  const { data: trendAppointments, isLoading: trendsLoading } = useQuery({
    queryKey: ["appointments", "trend", "doctor"],
    queryFn: () => {
      const end = new Date();
      const start = new Date();
      start.setDate(end.getDate() - 6);
      start.setHours(0, 0, 0, 0);
      return appointmentsApi
        .list({
          scheduled_after: start.toISOString(),
          scheduled_before: end.toISOString(),
          ordering: "scheduled_at",
        })
        .then((r) => r.data);
    },
  });

  const topRisk = patients?.results?.slice(0, 5) ?? [];

  const trendData = useMemo(() => {
    const end = new Date();
    const days = Array.from({ length: 7 }, (_, index) => {
      const day = new Date(end);
      day.setDate(end.getDate() - (6 - index));
      day.setHours(0, 0, 0, 0);
      return day;
    });

    const counts = new Map(
      days.map((day) => [
        day.toLocaleDateString("en-CA"),
        { date: day.toISOString().slice(0, 10), scheduled: 0, completed: 0 },
      ]),
    );

    (trendAppointments?.results ?? []).forEach((appt) => {
      const key = new Date(appt.scheduled_at).toLocaleDateString("en-CA");
      const entry = counts.get(key);
      if (!entry) return;
      entry.scheduled += 1;
      if (appt.status === "completed") entry.completed += 1;
    });

    return Array.from(counts.values());
  }, [trendAppointments]);

  if (isLoading && patientsLoading && trendsLoading) {
    return <PageSkeleton cards={4} rows={4} />;
  }

  return (
    <div className="space-y-8">
      <PageHeader
        title="Patient risk overview"
        description="Monitor adherence and prioritize high-risk patients"
      >
        <Button variant="outline" asChild className="rounded-xl">
          <Link to="/patients">View all patients</Link>
        </Button>
      </PageHeader>

      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Assigned patients" value={analytics?.patients_assigned ?? "—"} icon={Users} loading={isLoading} index={0} />
        <StatCard label="Appointments" value={analytics?.appointments_total ?? "—"} icon={Calendar} loading={isLoading} index={1} />
        <StatCard label="Completion rate" value={`${analytics?.completion_rate ?? "—"}%`} icon={TrendingUp} loading={isLoading} index={2} />
        <StatCard label="High-risk" value={analytics?.high_risk_patients ?? 0} icon={Activity} loading={isLoading} index={3} />
      </div>

      <div className="grid gap-8 lg:grid-cols-5">
        <div className="lg:col-span-2 space-y-4">
          <div>
            <h2 className="text-sm font-semibold tracking-tight">High-risk patients</h2>
            <p className="text-xs text-muted-foreground">Sorted by dropout risk score</p>
          </div>
          <div>
            {patientsLoading ? (
              <div className="space-y-2">
                {[1, 2, 3].map((i) => (
                  <Skeleton key={`risk-${i}`} className="h-12 rounded-lg" />
                ))}
              </div>
            ) : topRisk.length ? (
              <ul className="space-y-1">
                {topRisk.map((p) => {
                  const risk = riskLevel(p.risk_score ?? 0);
                  return (
                    <li key={p.id}>
                      <Link
                        to={`/patients/${p.id}`}
                        className="group flex items-center justify-between rounded-md p-2 text-sm transition-colors hover:bg-muted/50"
                      >
                        <div className="flex items-center gap-3">
                          <div
                            className={cn(
                              "flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-xs font-bold ring-1 ring-inset",
                              risk.className,
                            )}
                          >
                            {(p.risk_score ?? 0).toString()}
                          </div>
                          <p className="font-medium">{p.full_name}</p>
                        </div>
                        <span className="text-xs text-muted-foreground opacity-0 transition-opacity group-hover:opacity-100">
                          View
                        </span>
                      </Link>
                    </li>
                  );
                })}
              </ul>
            ) : (
              <p className="py-8 text-sm text-muted-foreground">No patients assigned yet</p>
            )}
          </div>
        </div>

        <div className="lg:col-span-3 space-y-4">
          <div>
            <h2 className="text-sm font-semibold tracking-tight">Weekly appointments</h2>
            <p className="text-xs text-muted-foreground">Scheduled vs completed</p>
          </div>
          <div className="h-[280px] w-full rounded-lg border border-border/60 bg-card p-4">
            {trendsLoading ? (
              <Skeleton className="h-full w-full rounded-lg" />
            ) : (
              <AppointmentTrendChart data={trendData} />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
