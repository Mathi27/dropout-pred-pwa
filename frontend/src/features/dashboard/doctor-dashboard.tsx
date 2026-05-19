import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { Activity, Calendar, TrendingUp, Users } from "lucide-react";
import { Link } from "react-router-dom";

import { analyticsApi } from "@/api/analytics";
import { patientsApi } from "@/api/patients";
import { AppointmentTrendChart } from "@/components/charts/appointment-trend-chart";
import { PageHeader } from "@/components/shared/page-header";
import { PageSkeleton } from "@/components/shared/page-skeleton";
import { StatCard } from "@/components/shared/stat-card";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

const MOCK_TRENDS = [
  { date: "2026-05-10", scheduled: 4, completed: 3 },
  { date: "2026-05-11", scheduled: 6, completed: 5 },
  { date: "2026-05-12", scheduled: 5, completed: 4 },
  { date: "2026-05-13", scheduled: 7, completed: 6 },
  { date: "2026-05-14", scheduled: 3, completed: 2 },
  { date: "2026-05-15", scheduled: 8, completed: 7 },
  { date: "2026-05-16", scheduled: 5, completed: 4 },
];

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

  const topRisk = patients?.results?.slice(0, 5) ?? [];

  if (isLoading && patientsLoading) {
    return <PageSkeleton cards={4} rows={4} />;
  }

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-8">
      <PageHeader
        title="Patient risk overview"
        description="Monitor adherence and prioritize high-risk patients"
      >
        <Button variant="outline" asChild className="rounded-xl">
          <Link to="/patients">View all patients</Link>
        </Button>
      </PageHeader>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Assigned patients" value={analytics?.patients_assigned ?? "—"} icon={Users} loading={isLoading} index={0} />
        <StatCard label="Appointments" value={analytics?.appointments_total ?? "—"} icon={Calendar} loading={isLoading} index={1} />
        <StatCard label="Completion rate" value={`${analytics?.completion_rate ?? "—"}%`} icon={TrendingUp} loading={isLoading} index={2} />
        <StatCard label="High-risk" value={analytics?.high_risk_patients ?? 0} icon={Activity} loading={isLoading} index={3} />
      </div>

      <div className="grid gap-6 lg:grid-cols-5">
        <Card className="glass-card border-0 lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-lg">High-risk patients</CardTitle>
            <CardDescription>Sorted by dropout risk score</CardDescription>
          </CardHeader>
          <CardContent>
            {patientsLoading ? (
              <div className="space-y-2">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="h-14 animate-pulse rounded-xl bg-muted" />
                ))}
              </div>
            ) : topRisk.length ? (
              <ul className="space-y-2">
                {topRisk.map((p, i) => {
                  const risk = riskLevel(p.risk_score ?? 0);
                  return (
                    <motion.li
                      key={p.id}
                      initial={{ opacity: 0, x: -8 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: i * 0.05 }}
                      whileHover={{ x: 4 }}
                    >
                      <Link
                        to={`/patients/${p.id}`}
                        className="flex items-center gap-3 rounded-xl border border-border/50 p-3 transition-all hover:border-primary/30 hover:bg-muted/30 hover:shadow-sm"
                      >
                        <div
                          className={cn(
                            "flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-sm font-bold ring-2",
                            risk.className,
                          )}
                        >
                          {(p.risk_score ?? 0).toString()}
                        </div>
                        <div className="min-w-0 flex-1">
                          <p className="truncate font-medium">{p.full_name}</p>
                          <p className="text-xs text-muted-foreground">{risk.label} risk</p>
                        </div>
                      </Link>
                    </motion.li>
                  );
                })}
              </ul>
            ) : (
              <p className="py-8 text-center text-sm text-muted-foreground">No patients assigned yet</p>
            )}
          </CardContent>
        </Card>

        <Card className="glass-card border-0 lg:col-span-3">
          <CardHeader>
            <CardTitle className="text-lg">Weekly appointments</CardTitle>
            <CardDescription>Scheduled vs completed</CardDescription>
          </CardHeader>
          <CardContent>
            <AppointmentTrendChart data={MOCK_TRENDS} />
          </CardContent>
        </Card>
      </div>
    </motion.div>
  );
}
