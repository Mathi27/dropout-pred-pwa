import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Calendar, CheckCircle, Clock, User } from "lucide-react";
import { toast } from "sonner";

import { appointmentsApi } from "@/api/appointments";
import { PageSkeleton } from "@/components/shared/page-skeleton";
import { StatCard } from "@/components/shared/stat-card";
import { StatusBadge } from "@/components/shared/status-badge";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export function ReceptionistDashboard() {
  const qc = useQueryClient();
  const today = new Date().toISOString().split("T")[0];

  const { data, isLoading, isError } = useQuery({
    queryKey: ["appointments", "today", today],
    queryFn: () => appointmentsApi.list({ date: today }).then((r) => r.data),
  });

  const markAttendance = useMutation({
    mutationFn: ({ id, attendance }: { id: string; attendance: string }) =>
      appointmentsApi.markAttendance(id, attendance),
    onMutate: async ({ id, attendance }) => {
      await qc.cancelQueries({ queryKey: ["appointments", "today", today] });
      const previousData = qc.getQueryData<any>(["appointments", "today", today]);
      
      if (previousData) {
        qc.setQueryData(["appointments", "today", today], {
          ...previousData,
          results: previousData.results.map((a: any) => 
            a.id === id ? { ...a, attendance } : a
          )
        });
      }
      return { previousData };
    },
    onError: (err, variables, context) => {
      if (context?.previousData) {
        qc.setQueryData(["appointments", "today", today], context.previousData);
      }
      toast.error("Failed to update attendance");
    },
    onSettled: () => {
      qc.invalidateQueries({ queryKey: ["appointments", "today", today] });
    },
    onSuccess: () => {
      toast.success("Attendance updated");
    },
  });

  const appointments = data?.results ?? [];
  const present = appointments.filter((a) => a.attendance === "present").length;
  const progress = appointments.length ? Math.round((present / appointments.length) * 100) : 0;

  if (isLoading) {
    return <PageSkeleton cards={3} rows={4} />;
  }

  if (isError) {
    return (
      <div className="flex flex-col items-center justify-center space-y-4 rounded-xl border border-destructive/20 bg-destructive/5 p-8 text-center text-destructive">
        <Clock className="h-10 w-10 opacity-80" />
        <div>
          <h2 className="text-lg font-semibold">Failed to load schedule</h2>
          <p className="text-sm opacity-80">Could not retrieve appointments. Please verify your permissions or try refreshing.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Today's schedule</h1>
          <p className="text-sm text-muted-foreground">{new Date().toLocaleDateString("en-IN", { dateStyle: "long" })}</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-right">
            <p className="text-sm font-medium">{progress}% checked in</p>
            <p className="text-xs text-muted-foreground">{present} of {appointments.length} patients</p>
          </div>
          <div className="h-2 w-32 overflow-hidden rounded-full bg-muted">
            <div className="h-full bg-foreground transition-all duration-500" style={{ width: `${progress}%` }} />
          </div>
        </div>
      </div>

      <div className="grid gap-3 sm:grid-cols-3">
        <StatCard label="Total today" value={appointments.length} icon={Calendar} index={0} />
        <StatCard label="Present" value={present} icon={CheckCircle} index={1} />
        <StatCard label="Pending" value={appointments.length - present} icon={Clock} index={2} />
      </div>

      <div className="space-y-4">
        <div>
          <h2 className="text-sm font-semibold tracking-tight">Daily appointments</h2>
        </div>
        <div className="divide-y rounded-lg border border-border/60 bg-card">
          {appointments.length ? (
            appointments.map((a) => (
              <div
                key={a.id}
                className={cn(
                  "flex items-center justify-between p-4 transition-colors",
                  a.attendance === "present" ? "bg-muted/10" : "hover:bg-muted/30",
                )}
              >
                <div className="flex items-center gap-4">
                  <p className="w-16 shrink-0 text-sm font-medium text-muted-foreground">
                    {new Date(a.scheduled_at).toLocaleTimeString("en-IN", {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </p>
                  <div>
                    <p className="font-semibold text-sm">{a.patient_detail?.full_name ?? "Patient"}</p>
                    <div className="mt-1 flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
                      <span>Dr. {a.doctor_detail?.full_name ?? "Unassigned"}</span>
                      <span>·</span>
                      <StatusBadge status={a.status} />
                      {a.attendance !== "pending" && (
                        <>
                          <span>·</span>
                          <StatusBadge status={a.attendance} />
                        </>
                      )}
                    </div>
                  </div>
                </div>
                <div className="flex gap-2 shrink-0">
                  <Button
                    size="sm"
                    variant={a.attendance === "present" ? "default" : "outline"}
                    className="h-8"
                    onClick={() => markAttendance.mutate({ id: a.id, attendance: "present" })}
                  >
                    Present
                  </Button>
                  <Button
                    size="sm"
                    variant={a.attendance === "absent" ? "destructive" : "outline"}
                    className="h-8"
                    onClick={() => markAttendance.mutate({ id: a.id, attendance: "absent" })}
                  >
                    Absent
                  </Button>
                </div>
              </div>
            ))
          ) : (
            <p className="p-8 text-center text-sm text-muted-foreground">No appointments scheduled for today</p>
          )}
        </div>
      </div>
    </div>
  );
}
