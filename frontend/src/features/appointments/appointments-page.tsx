import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { Calendar } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

import { appointmentsApi } from "@/api/appointments";
import { patientsApi } from "@/api/patients";
import { doctorsApi } from "@/api/resources";
import { EmptyState } from "@/components/shared/empty-state";
import { PageHeader } from "@/components/shared/page-header";
import { PageSkeleton } from "@/components/shared/page-skeleton";
import { StatusBadge } from "@/components/shared/status-badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuthStore } from "@/stores/auth-store";

function toDateTimeLocal(value: string) {
  const date = new Date(value);
  const pad = (part: number) => String(part).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(
    date.getHours(),
  )}:${pad(date.getMinutes())}`;
}

export function AppointmentsPage() {
  const role = useAuthStore((s) => s.user?.role);
  const qc = useQueryClient();
  const canCreate = role === "patient" || role === "receptionist" || role === "admin";
  const canCreateForOthers = role === "receptionist" || role === "admin";

  const [scheduledAt, setScheduledAt] = useState("");
  const [durationMinutes, setDurationMinutes] = useState("30");
  const [reason, setReason] = useState("");
  const [patientId, setPatientId] = useState("");
  const [doctorId, setDoctorId] = useState("");
  const [rescheduleId, setRescheduleId] = useState<string | null>(null);
  const [rescheduleAt, setRescheduleAt] = useState("");

  const { data, isLoading, isError } = useQuery({
    queryKey: ["appointments"],
    queryFn: () => appointmentsApi.list({ ordering: "scheduled_at" }).then((r) => r.data),
  });

  const { data: patientProfile } = useQuery({
    queryKey: ["patient-me"],
    queryFn: () => patientsApi.me().then((r) => r.data),
    enabled: role === "patient",
  });

  const { data: patientOptions } = useQuery({
    queryKey: ["patients", "list"],
    queryFn: () => patientsApi.list({ ordering: "user__last_name" }).then((r) => r.data),
    enabled: canCreateForOthers,
  });

  const { data: doctorOptions } = useQuery({
    queryKey: ["doctors", "list"],
    queryFn: () => doctorsApi.list({ ordering: "user__last_name" }).then((r) => r.data),
    enabled: canCreateForOthers,
  });

  const createAppointment = useMutation({
    mutationFn: () => {
      const scheduledIso = scheduledAt ? new Date(scheduledAt).toISOString() : "";
      if (!scheduledIso) {
        return Promise.reject(new Error("scheduled_at required"));
      }
      const payload: Record<string, string | number> = {
        scheduled_at: scheduledIso,
        duration_minutes: Number(durationMinutes || 30),
      };
      if (reason) payload.reason = reason;
      if (canCreateForOthers) {
        payload.patient_id = patientId;
        if (doctorId) payload.doctor_id = doctorId;
      } else if (patientProfile?.id) {
        payload.patient_id = patientProfile.id;
      }
      return appointmentsApi.create(payload as any).then((r) => r.data);
    },
    onSuccess: () => {
      toast.success("Appointment booked");
      setScheduledAt("");
      setDurationMinutes("30");
      setReason("");
      setPatientId("");
      setDoctorId("");
      qc.invalidateQueries({ queryKey: ["appointments"], exact: false });
      qc.invalidateQueries({ queryKey: ["admin-analytics"] });
      qc.invalidateQueries({ queryKey: ["doctor-analytics"] });
    },
    onError: () => {
      toast.error("Failed to book appointment");
    },
  });

  const reschedule = useMutation({
    mutationFn: ({ id, scheduledAt: nextAt }: { id: string; scheduledAt: string }) =>
      appointmentsApi.reschedule(id, new Date(nextAt).toISOString()),
    onSuccess: () => {
      toast.success("Appointment rescheduled");
      setRescheduleId(null);
      setRescheduleAt("");
      qc.invalidateQueries({ queryKey: ["appointments"], exact: false });
      qc.invalidateQueries({ queryKey: ["admin-analytics"] });
      qc.invalidateQueries({ queryKey: ["doctor-analytics"] });
    },
    onError: () => {
      toast.error("Failed to reschedule appointment");
    },
  });

  const cancel = useMutation({
    mutationFn: (id: string) => appointmentsApi.update(id, { status: "cancelled" }),
    onMutate: async (id) => {
      await qc.cancelQueries({ queryKey: ["appointments"] });
      const previousData = qc.getQueryData<any>(["appointments"]);
      
      if (previousData) {
        qc.setQueryData(["appointments"], {
          ...previousData,
          results: previousData.results.map((a: any) => 
            a.id === id ? { ...a, status: "cancelled" } : a
          )
        });
      }
      return { previousData };
    },
    onError: (err, variables, context) => {
      if (context?.previousData) {
        qc.setQueryData(["appointments"], context.previousData);
      }
      toast.error("Failed to cancel appointment");
    },
    onSettled: () => {
      qc.invalidateQueries({ queryKey: ["appointments"], exact: false });
      qc.invalidateQueries({ queryKey: ["admin-analytics"] });
      qc.invalidateQueries({ queryKey: ["doctor-analytics"] });
    },
    onSuccess: () => {
      toast.success("Appointment cancelled");
    },
  });

  const appointments = data?.results ?? [];

  const handleCreate = (event: React.FormEvent) => {
    event.preventDefault();
    if (canCreateForOthers && !patientId) {
      toast.error("Select a patient");
      return;
    }
    if (!scheduledAt) {
      toast.error("Select a date and time");
      return;
    }
    createAppointment.mutate();
  };

  const handleReschedule = (id: string) => {
    if (!rescheduleAt) {
      toast.error("Select a new time");
      return;
    }
    reschedule.mutate({ id, scheduledAt: rescheduleAt });
  };

  const createDisabled =
    createAppointment.isPending ||
    !scheduledAt ||
    (canCreateForOthers && !patientId) ||
    (!canCreateForOthers && !patientProfile?.id);

  if (isLoading) {
    return <PageSkeleton cards={0} rows={4} />;
  }

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-8">
      <PageHeader title="Appointments" description="View and manage your visits" />

      {canCreate && (
        <div className="rounded-lg border border-border/60 bg-card p-4">
          <form onSubmit={handleCreate} className="grid gap-4 md:grid-cols-2">
            {canCreateForOthers ? (
              <div className="space-y-2">
                <Label>Patient</Label>
                <select
                  className="h-10 w-full rounded-lg border border-border/60 bg-background px-3 text-sm"
                  value={patientId}
                  onChange={(event) => setPatientId(event.target.value)}
                  required
                >
                  <option value="">Select patient</option>
                  {patientOptions?.results?.map((patient) => (
                    <option key={patient.id} value={patient.id}>
                      {patient.full_name}
                    </option>
                  ))}
                </select>
              </div>
            ) : (
              <div className="space-y-2">
                <Label>Patient</Label>
                <Input value={patientProfile?.full_name ?? "Loading..."} disabled />
              </div>
            )}

            {canCreateForOthers && (
              <div className="space-y-2">
                <Label>Doctor (optional)</Label>
                <select
                  className="h-10 w-full rounded-lg border border-border/60 bg-background px-3 text-sm"
                  value={doctorId}
                  onChange={(event) => setDoctorId(event.target.value)}
                >
                  <option value="">Auto-assign</option>
                  {doctorOptions?.results?.map((doctor) => (
                    <option key={doctor.id} value={doctor.id}>
                      {doctor.full_name}
                    </option>
                  ))}
                </select>
              </div>
            )}

            <div className="space-y-2">
              <Label>Date & time</Label>
              <Input
                type="datetime-local"
                value={scheduledAt}
                onChange={(event) => setScheduledAt(event.target.value)}
                required
              />
            </div>

            <div className="space-y-2">
              <Label>Duration (minutes)</Label>
              <Input
                type="number"
                min={10}
                step={5}
                value={durationMinutes}
                onChange={(event) => setDurationMinutes(event.target.value)}
              />
            </div>

            <div className="space-y-2 md:col-span-2">
              <Label>Reason (optional)</Label>
              <Input value={reason} onChange={(event) => setReason(event.target.value)} />
            </div>

            <div className="md:col-span-2 flex justify-end">
              <Button type="submit" className="rounded-lg" disabled={createDisabled}>
                {createAppointment.isPending ? "Booking..." : "Book appointment"}
              </Button>
            </div>
          </form>
        </div>
      )}

      {isError ? (
        <p className="rounded-xl border border-destructive/30 bg-destructive/5 p-4 text-sm text-destructive">
          Failed to load appointments
        </p>
      ) : appointments.length === 0 ? (
        <EmptyState
          icon={Calendar}
          title="No appointments"
          description="Your scheduled visits will appear here."
        />
      } else (
        <div className="divide-y rounded-lg border border-border/60 bg-card">
          {appointments.map((a) => {
            const isPast = new Date(a.scheduled_at) < new Date();
            const canModify = role !== "doctor" && !isPast && a.status !== "cancelled";
            const isRescheduling = rescheduleId === a.id;
            return (
              <div key={a.id} className="space-y-3 p-4">
                <div className="flex flex-wrap items-center justify-between gap-4">
                  <div className="flex items-center gap-4">
                    <p className="w-16 shrink-0 text-sm font-medium text-muted-foreground">
                      {new Date(a.scheduled_at).toLocaleTimeString("en-IN", {
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </p>
                    <div>
                      <p className="font-semibold text-sm">
                        {new Date(a.scheduled_at).toLocaleDateString("en-IN", {
                          dateStyle: "medium",
                        })}
                      </p>
                      <div className="mt-1 flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
                        <span>{a.patient_detail?.full_name ?? "—"}</span>
                        <span>·</span>
                        <span>Dr. {a.doctor_detail?.full_name ?? "TBD"}</span>
                        <span>·</span>
                        <StatusBadge status={a.status} />
                        <StatusBadge status={a.attendance} />
                      </div>
                    </div>
                  </div>

                  {canModify && (
                    <div className="flex flex-wrap gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        className="h-8"
                        onClick={() => {
                          setRescheduleId(a.id);
                          setRescheduleAt(toDateTimeLocal(a.scheduled_at));
                        }}
                        disabled={reschedule.isPending}
                      >
                        Reschedule
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        className="h-8"
                        onClick={() => cancel.mutate(a.id)}
                        disabled={cancel.isPending}
                      >
                        Cancel
                      </Button>
                    </div>
                  )}
                </div>

                {isRescheduling && (
                  <div className="flex flex-wrap items-end gap-3 rounded-lg border border-border/60 bg-muted/20 p-3">
                    <div className="space-y-2">
                      <Label>New time</Label>
                      <Input
                        type="datetime-local"
                        value={rescheduleAt}
                        onChange={(event) => setRescheduleAt(event.target.value)}
                      />
                    </div>
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        className="h-9"
                        onClick={() => handleReschedule(a.id)}
                        disabled={reschedule.isPending}
                      >
                        {reschedule.isPending ? "Updating..." : "Confirm"}
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        className="h-9"
                        onClick={() => {
                          setRescheduleId(null);
                          setRescheduleAt("");
                        }}
                      >
                        Dismiss
                      </Button>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </motion.div>
  );
}
