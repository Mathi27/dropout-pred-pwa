import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { Calendar, CheckCircle, Clock, User } from "lucide-react";
import { toast } from "sonner";

import { appointmentsApi } from "@/api/appointments";
import { PageHeader } from "@/components/shared/page-header";
import { PageSkeleton } from "@/components/shared/page-skeleton";
import { StatCard } from "@/components/shared/stat-card";
import { StatusBadge } from "@/components/shared/status-badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

export function ReceptionistDashboard() {
  const qc = useQueryClient();
  const today = new Date().toISOString().split("T")[0];

  const { data, isLoading } = useQuery({
    queryKey: ["appointments", "today", today],
    queryFn: () => appointmentsApi.list({ date: today }).then((r) => r.data),
  });

  const markAttendance = useMutation({
    mutationFn: ({ id, attendance }: { id: string; attendance: string }) =>
      appointmentsApi.markAttendance(id, attendance),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["appointments"] });
      toast.success("Attendance updated");
    },
  });

  const appointments = data?.results ?? [];
  const present = appointments.filter((a) => a.attendance === "present").length;
  const progress = appointments.length ? Math.round((present / appointments.length) * 100) : 0;

  if (isLoading) {
    return <PageSkeleton cards={3} rows={4} />;
  }

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-8">
      <PageHeader
        title="Today's schedule"
        description={new Date().toLocaleDateString("en-IN", { weekday: "long", dateStyle: "long" })}
      />

      <Card className="hero-gradient border-0 shadow-card">
        <CardContent className="flex flex-col gap-4 p-6 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-sm text-muted-foreground">Check-in progress</p>
            <p className="text-3xl font-bold tracking-tight">{progress}%</p>
            <p className="text-sm text-muted-foreground">
              {present} of {appointments.length} patients checked in
            </p>
          </div>
          <div className="h-3 w-full max-w-xs overflow-hidden rounded-full bg-muted sm:w-48">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              className="h-full rounded-full bg-gradient-to-r from-primary to-teal-400"
            />
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-4 sm:grid-cols-3">
        <StatCard label="Total today" value={appointments.length} icon={Calendar} index={0} />
        <StatCard label="Present" value={present} icon={CheckCircle} index={1} />
        <StatCard label="Pending" value={appointments.length - present} icon={Clock} index={2} />
      </div>

      <Card className="glass-card border-0">
        <CardHeader>
          <CardTitle className="text-lg">Daily appointments</CardTitle>
          <CardDescription>Mark attendance for each patient</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {appointments.length ? (
            appointments.map((a, i) => (
              <motion.div
                key={a.id}
                layout
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.04 }}
                className={cn(
                  "flex flex-col gap-3 rounded-2xl border border-border/50 p-4 transition-all sm:flex-row sm:items-center sm:justify-between",
                  a.attendance === "present" && "border-primary/30 bg-primary/5",
                )}
              >
                <div className="flex items-start gap-3">
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-muted">
                    <User className="h-5 w-5 text-muted-foreground" />
                  </div>
                  <div>
                    <p className="font-semibold">{a.patient_detail?.full_name ?? "Patient"}</p>
                    <p className="text-sm text-muted-foreground">
                      {new Date(a.scheduled_at).toLocaleTimeString("en-IN", {
                        hour: "2-digit",
                        minute: "2-digit",
                      })}{" "}
                      · Dr. {a.doctor_detail?.full_name ?? "Unassigned"}
                    </p>
                    <div className="mt-2 flex gap-2">
                      <StatusBadge status={a.status} />
                      <StatusBadge status={a.attendance} />
                    </div>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button
                    size="sm"
                    variant={a.attendance === "present" ? "default" : "outline"}
                    className="rounded-lg"
                    onClick={() => markAttendance.mutate({ id: a.id, attendance: "present" })}
                  >
                    Present
                  </Button>
                  <Button
                    size="sm"
                    variant={a.attendance === "absent" ? "destructive" : "outline"}
                    className="rounded-lg"
                    onClick={() => markAttendance.mutate({ id: a.id, attendance: "absent" })}
                  >
                    Absent
                  </Button>
                </div>
              </motion.div>
            ))
          ) : (
            <p className="py-12 text-center text-sm text-muted-foreground">
              No appointments scheduled for today
            </p>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}
