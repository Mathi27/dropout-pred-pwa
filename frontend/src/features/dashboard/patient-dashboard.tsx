import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import {
  ArrowRight,
  Bell,
  Calendar,
  CalendarPlus,
  CreditCard,
  HeartPulse,
  MessageSquare,
} from "lucide-react";
import { Link } from "react-router-dom";

import { appointmentsApi } from "@/api/appointments";
import { notificationsApi } from "@/api/notifications";
import { patientTreatmentsApi, paymentsApi } from "@/api/resources";
import { PageHeader } from "@/components/shared/page-header";
import { StatCard } from "@/components/shared/stat-card";
import { StatusBadge } from "@/components/shared/status-badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useAuthStore } from "@/stores/auth-store";

const container = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.06 } },
};

export function PatientDashboard() {
  const user = useAuthStore((s) => s.user);

  const { data: appointments, isLoading: apptLoading } = useQuery({
    queryKey: ["appointments", "upcoming"],
    queryFn: () => appointmentsApi.list({ ordering: "scheduled_at" }).then((r) => r.data),
  });

  const { data: treatments, isLoading: txLoading } = useQuery({
    queryKey: ["patient-treatments"],
    queryFn: () => patientTreatmentsApi.list().then((r) => r.data),
  });

  const { data: notifications, isLoading: notifLoading } = useQuery({
    queryKey: ["notifications"],
    queryFn: () => notificationsApi.list({ is_read: "false" }).then((r) => r.data),
  });

  const { data: payments } = useQuery({
    queryKey: ["payments"],
    queryFn: () => paymentsApi.list().then((r) => r.data),
  });

  const upcoming = appointments?.results
    ?.filter((a) => new Date(a.scheduled_at) >= new Date() && a.status !== "cancelled")
    .slice(0, 3);

  const nextAppt = upcoming?.[0];
  const recentNotifs = notifications?.results?.slice(0, 4) ?? [];

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="space-y-8">
      <PageHeader
        title={`Welcome back, ${user?.first_name || "Patient"}`}
        description="Your treatment journey at a glance"
      />

      {nextAppt && !apptLoading && (
        <motion.div variants={{ hidden: { opacity: 0, y: 12 }, show: { opacity: 1, y: 0 } }}>
          <Card className="hero-gradient overflow-hidden border-0 shadow-elevated">
            <CardContent className="flex flex-col gap-4 p-6 sm:flex-row sm:items-center sm:justify-between">
              <div className="space-y-2">
                <p className="text-xs font-semibold uppercase tracking-wider text-primary">
                  Next appointment
                </p>
                <p className="text-2xl font-bold tracking-tight">
                  {new Date(nextAppt.scheduled_at).toLocaleString("en-IN", {
                    weekday: "long",
                    dateStyle: "medium",
                    timeStyle: "short",
                  })}
                </p>
                <StatusBadge status={nextAppt.status} />
              </div>
              <Button asChild className="shrink-0 rounded-xl">
                <Link to="/appointments">
                  View details
                  <ArrowRight className="ml-1 h-4 w-4" />
                </Link>
              </Button>
            </CardContent>
          </Card>
        </motion.div>
      )}

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Upcoming visits" value={upcoming?.length ?? 0} icon={Calendar} loading={apptLoading} index={0} />
        <StatCard
          label="Active treatments"
          value={treatments?.results?.filter((t) => t.status !== "completed").length ?? 0}
          icon={HeartPulse}
          loading={txLoading}
          index={1}
        />
        <StatCard label="Unread alerts" value={notifications?.count ?? 0} icon={Bell} index={2} />
        <StatCard label="Payments" value={payments?.count ?? 0} icon={CreditCard} index={3} />
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        {[
          { label: "Book visit", icon: CalendarPlus, href: "/appointments" },
          { label: "Messages", icon: MessageSquare, href: "/notifications" },
          { label: "Payments", icon: CreditCard, href: "/appointments" },
        ].map((action) => (
          <Button key={action.label} variant="outline" asChild className="h-auto justify-start gap-3 rounded-2xl border-border/60 p-4">
            <Link to={action.href}>
              <action.icon className="h-5 w-5 text-primary" />
              <span className="font-medium">{action.label}</span>
            </Link>
          </Button>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card className="glass-card border-0">
          <CardHeader>
            <CardTitle className="text-lg">Upcoming appointments</CardTitle>
            <CardDescription>Your scheduled visits</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {apptLoading ? (
              <Skeleton className="h-16 w-full rounded-xl" />
            ) : upcoming?.length ? (
              upcoming.map((a, i) => (
                <motion.div
                  key={a.id}
                  initial={{ opacity: 0, x: -8 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.05 }}
                  className="flex items-center justify-between rounded-xl border border-border/50 bg-background/50 p-4 transition-colors hover:bg-muted/30"
                >
                  <div>
                    <p className="font-medium">
                      {new Date(a.scheduled_at).toLocaleString("en-IN", {
                        dateStyle: "medium",
                        timeStyle: "short",
                      })}
                    </p>
                    <p className="mt-1 text-sm text-muted-foreground">
                      Dr. {a.doctor_detail?.full_name ?? "TBD"}
                    </p>
                  </div>
                  <StatusBadge status={a.status} />
                </motion.div>
              ))
            ) : (
              <p className="py-4 text-center text-sm text-muted-foreground">No upcoming appointments</p>
            )}
          </CardContent>
        </Card>

        <Card className="glass-card border-0">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle className="text-lg">Notifications</CardTitle>
              <CardDescription>Recent alerts & reminders</CardDescription>
            </div>
            <Button variant="ghost" size="sm" asChild className="rounded-lg">
              <Link to="/notifications">View all</Link>
            </Button>
          </CardHeader>
          <CardContent className="space-y-2">
            {notifLoading ? (
              <Skeleton className="h-20 w-full rounded-xl" />
            ) : recentNotifs.length ? (
              recentNotifs.map((n) => (
                <div
                  key={n.id}
                  className="rounded-xl border border-border/40 p-3 transition-colors hover:bg-muted/30"
                >
                  <p className="text-sm font-medium">{n.title}</p>
                  <p className="mt-0.5 line-clamp-1 text-xs text-muted-foreground">{n.body}</p>
                </div>
              ))
            ) : (
              <p className="py-6 text-center text-sm text-muted-foreground">All caught up</p>
            )}
          </CardContent>
        </Card>
      </div>

      <Card className="glass-card border-0">
        <CardHeader>
          <CardTitle className="text-lg">Treatment progress</CardTitle>
          <CardDescription>Track your adherence journey</CardDescription>
        </CardHeader>
        <CardContent className="space-y-5">
          {txLoading ? (
            <Skeleton className="h-16 w-full rounded-xl" />
          ) : treatments?.results?.length ? (
            treatments.results.map((t) => (
              <div key={t.id}>
                <div className="mb-2 flex justify-between text-sm">
                  <span className="font-medium">{t.treatment_detail?.name ?? "Treatment"}</span>
                  <span className="font-semibold text-primary">{t.progress_percent}%</span>
                </div>
                <div className="h-2.5 overflow-hidden rounded-full bg-muted">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${t.progress_percent}%` }}
                    transition={{ duration: 0.8, ease: "easeOut" }}
                    className="h-full rounded-full bg-gradient-to-r from-primary to-teal-400"
                  />
                </div>
              </div>
            ))
          ) : (
            <p className="text-sm text-muted-foreground">No active treatments</p>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}
