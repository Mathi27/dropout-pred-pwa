import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { Calendar } from "lucide-react";
import { toast } from "sonner";

import { appointmentsApi } from "@/api/appointments";
import { EmptyState } from "@/components/shared/empty-state";
import { PageHeader } from "@/components/shared/page-header";
import { PageSkeleton } from "@/components/shared/page-skeleton";
import { StatusBadge } from "@/components/shared/status-badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useAuthStore } from "@/stores/auth-store";

export function AppointmentsPage() {
  const role = useAuthStore((s) => s.user?.role);
  const qc = useQueryClient();

  const { data, isLoading, isError } = useQuery({
    queryKey: ["appointments"],
    queryFn: () => appointmentsApi.list({ ordering: "scheduled_at" }).then((r) => r.data),
  });

  const cancel = useMutation({
    mutationFn: (id: string) => appointmentsApi.update(id, { status: "cancelled" }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["appointments"] });
      toast.success("Appointment cancelled");
    },
  });

  const appointments = data?.results ?? [];

  if (isLoading) {
    return <PageSkeleton cards={0} rows={4} />;
  }

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-8">
      <PageHeader title="Appointments" description="View and manage your visits" />

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
      ) : (
        <div className="space-y-3">
          {appointments.map((a, i) => (
            <motion.div
              key={a.id}
              layout
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.03 }}
            >
              <Card className="glass-card border-0 transition-shadow hover:shadow-elevated">
                <CardContent className="flex flex-col gap-4 p-5 sm:flex-row sm:items-center sm:justify-between">
                  <div className="space-y-2">
                    <p className="text-lg font-semibold">
                      {new Date(a.scheduled_at).toLocaleString("en-IN", {
                        dateStyle: "medium",
                        timeStyle: "short",
                      })}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {a.patient_detail?.full_name ?? "—"} · Dr. {a.doctor_detail?.full_name ?? "TBD"}
                    </p>
                    <div className="flex flex-wrap gap-2">
                      <StatusBadge status={a.status} />
                      <StatusBadge status={a.attendance} />
                    </div>
                  </div>
                  {role !== "patient" && a.status !== "cancelled" && (
                    <Button
                      variant="outline"
                      size="sm"
                      className="rounded-lg"
                      onClick={() => cancel.mutate(a.id)}
                    >
                      Cancel
                    </Button>
                  )}
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      )}
    </motion.div>
  );
}
