import { useMutation, useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { useParams } from "react-router-dom";

import { aiPredictionsApi } from "@/api/ai-predictions";
import { patientsApi } from "@/api/patients";
import { clinicalNotesApi, patientTreatmentsApi } from "@/api/resources";
import { PageHeader } from "@/components/shared/page-header";
import { AdherenceScoreCard } from "@/components/shared/adherence-score-card";
import { JourneyMap } from "@/components/shared/journey-map";
import { JourneyStatCard } from "@/components/shared/journey-stat-card";
import { PatientRiskTimeline } from "@/components/shared/patient-risk-timeline";
import { PredictionHistoryTimeline } from "@/components/shared/prediction-history-timeline";
import { RiskBadge } from "@/components/shared/risk-badge";
import { StatusBadge } from "@/components/shared/status-badge";
import { DeliveryStatusBadge } from "@/components/shared/delivery-status-badge";
import { ShapExplanationCard } from "@/components/shared/shap-explanation-card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useAuthStore } from "@/stores/auth-store";
import { useState } from "react";
import { toast } from "sonner";
import { useQueryClient } from "@tanstack/react-query";

export function PatientDetailPage() {
  const { id } = useParams<{ id: string }>();

  const { data: patient, isLoading } = useQuery({
    queryKey: ["patient", id],
    queryFn: () => patientsApi.get(id!).then((r) => r.data),
    enabled: !!id,
  });

  const { data: treatments } = useQuery({
    queryKey: ["patient-treatments", id],
    queryFn: () => patientTreatmentsApi.list({ patient: id! }).then((r) => r.data),
    enabled: !!id,
  });

  const { data: notes } = useQuery({
    queryKey: ["clinical-notes", id],
    queryFn: () => clinicalNotesApi.list({ patient: id! }).then((r) => r.data),
    enabled: !!id,
  });

  const {
    data: prediction,
    isError: predictionError,
    refetch: refetchPrediction,
  } = useQuery({
    queryKey: ["ai-risk", id],
    queryFn: () => aiPredictionsApi.getRisk(id!).then((r) => r.data),
    enabled: !!id,
    retry: false,
  });

  const { data: explanation, refetch: refetchExplanation } = useQuery({
    queryKey: ["ai-shap", id],
    queryFn: () => aiPredictionsApi.getShap(id!).then((r) => r.data),
    enabled: !!prediction,
    retry: false,
  });

  const { data: history, refetch: refetchHistory } = useQuery({
    queryKey: ["ai-history", id],
    queryFn: () => aiPredictionsApi.history(id!, 8).then((r) => r.data),
    enabled: !!id,
  });

  const { data: journey, refetch: refetchJourney } = useQuery({
    queryKey: ["ai-journey", id],
    queryFn: () => aiPredictionsApi.journey(id!, 180).then((r) => r.data),
    enabled: !!id,
  });

  const { mutateAsync: runPrediction, isPending } = useMutation({
    mutationFn: () => aiPredictionsApi.generate(id!).then((r) => r.data),
    onSuccess: () => {
      refetchPrediction();
      refetchExplanation();
      refetchHistory();
      refetchJourney();
    },
  });

  const qc = useQueryClient();
  const role = useAuthStore((s) => s.user?.role);
  const [noteContent, setNoteContent] = useState("");
  const [noteDate, setNoteDate] = useState(new Date().toISOString().split("T")[0]);

  const addNote = useMutation({
    mutationFn: (newNote: { patient_id: string; content: string; visit_date: string }) =>
      clinicalNotesApi.create(newNote),
    onMutate: async (newNote) => {
      await qc.cancelQueries({ queryKey: ["clinical-notes", id] });
      const previousNotes = qc.getQueryData<{ results: any[] }>(["clinical-notes", id]);
      qc.setQueryData<{ results: any[] }>(["clinical-notes", id], (old) => ({
        ...old,
        results: [{ ...newNote, id: "temp-id", visit_date: newNote.visit_date }, ...(old?.results ?? [])],
      }));
      return { previousNotes };
    },
    onSuccess: () => {
      toast.success("Note added");
      setNoteContent("");
      setNoteDate(new Date().toISOString().split("T")[0]);
    },
    onError: (err, newNote, context) => {
      toast.error("Failed to add note");
      if (context?.previousNotes) {
        qc.setQueryData(["clinical-notes", id], context.previousNotes);
      }
    },
    onSettled: () => {
      qc.invalidateQueries({ queryKey: ["clinical-notes", id] });
      qc.invalidateQueries({ queryKey: ["admin-analytics"] });
      qc.invalidateQueries({ queryKey: ["doctor-analytics"] });
    },
  });

  const updateProgress = useMutation({
    mutationFn: ({ tId, progress }: { tId: string; progress: number }) =>
      patientTreatmentsApi.updateProgress(tId, progress),
    onMutate: async ({ tId, progress }) => {
      await qc.cancelQueries({ queryKey: ["patient-treatments", id] });
      const previousTreatments = qc.getQueryData<{ results: any[] }>(["patient-treatments", id]);
      qc.setQueryData<{ results: any[] }>(["patient-treatments", id], (old) => ({
        ...old,
        results: old?.results?.map((t) => (t.id === tId ? { ...t, progress_percent: progress } : t)) ?? [],
      }));
      return { previousTreatments };
    },
    onSuccess: () => {
      toast.success("Progress updated");
    },
    onError: (err, newProgress, context) => {
      toast.error("Failed to update progress");
      if (context?.previousTreatments) {
        qc.setQueryData(["patient-treatments", id], context.previousTreatments);
      }
    },
    onSettled: () => {
      qc.invalidateQueries({ queryKey: ["patient-treatments", id] });
      qc.invalidateQueries({ queryKey: ["admin-analytics"] });
      qc.invalidateQueries({ queryKey: ["doctor-analytics"] });
    },
  });

  if (isLoading) return <Skeleton className="h-64 w-full" />;
  if (!patient) return <p>Patient not found</p>;

  const fallbackScore = prediction?.risk_score ?? patient.risk_score;

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
      <PageHeader
        title={patient.full_name}
        description={
          prediction?.risk_score
            ? `Dropout risk: ${prediction.risk_score}%`
            : predictionError
              ? "No prediction generated yet"
              : fallbackScore !== undefined
                ? `Dropout risk: ${fallbackScore}%`
                : "Dropout risk: —"
        }
      >
        <Button
          variant="outline"
          className="rounded-xl"
          onClick={() => runPrediction()}
          disabled={isPending}
        >
          {isPending ? "Running..." : "Run prediction"}
        </Button>
      </PageHeader>

      <div className="grid gap-8 lg:grid-cols-12">
        <div className="space-y-10 lg:col-span-8">
          <section>
            <h2 className="mb-4 text-xs font-semibold tracking-widest uppercase text-muted-foreground">Journey Adherence</h2>
            <div className="grid gap-4 sm:grid-cols-3">
              <AdherenceScoreCard
                score={journey?.adherence_score}
                stage={journey?.adherence_stage}
              />
              <JourneyStatCard
                label="Visit adherence"
                value={journey ? `${journey.appointment_summary.completed}/${journey.appointment_summary.total}` : "—"}
                helper={journey ? `${journey.appointment_summary.missed} missed visits` : undefined}
              />
              <JourneyStatCard
                label="Engagement"
                value={journey ? `${journey.communication_engagement.read_rate}%` : "—"}
                helper={journey ? `${journey.communication_engagement.read} reads` : undefined}
              />
            </div>
          </section>

          <section>
            <h2 className="mb-4 text-xs font-semibold tracking-widest uppercase text-muted-foreground">Journey Map</h2>
            <div className="rounded-xl border border-border/50 bg-card/20 p-4 md:p-6">
              <JourneyMap milestones={journey?.milestones ?? {}} />
            </div>
          </section>

          <section>
            <h2 className="mb-4 text-xs font-semibold tracking-widest uppercase text-muted-foreground">Patient Timeline</h2>
            <div className="rounded-xl border border-border/50 bg-card/20 p-4 md:p-6">
              <PatientRiskTimeline events={journey?.timeline ?? []} />
            </div>
          </section>

          <section>
            <h2 className="mb-4 text-xs font-semibold tracking-widest uppercase text-muted-foreground">Prediction History</h2>
            <div className="rounded-xl border border-border/50 bg-card/20 p-4 md:p-6">
              <PredictionHistoryTimeline predictions={history ?? []} />
            </div>
          </section>
        </div>

        <div className="space-y-10 lg:col-span-4">
          <section>
            <h2 className="mb-4 text-xs font-semibold tracking-widest uppercase text-muted-foreground">Risk Overview</h2>
            <div className="space-y-6 rounded-xl border border-border/50 bg-card/20 p-5">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-muted-foreground uppercase tracking-widest mb-1">Probability</p>
                  <p className="text-3xl font-semibold tracking-tight">
                    {prediction ? `${Math.round(prediction.probability * 100)}%` : "—"}
                  </p>
                </div>
                <RiskBadge
                  score={prediction?.risk_score ?? patient.risk_score}
                  level={prediction?.risk_level ?? patient.risk_level}
                  className="text-sm px-3 py-1.5"
                />
              </div>
              <div className="border-t border-border/50 pt-4">
                <ShapExplanationCard explanation={explanation} />
              </div>
            </div>
          </section>

          <section>
            <h2 className="mb-4 text-xs font-semibold tracking-widest uppercase text-muted-foreground">Treatments</h2>
            <div className="space-y-6">
              {treatments?.results?.map((t) => (
                <div key={t.id} className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="font-medium text-foreground">{t.treatment_detail?.name}</span>
                    <span className="text-muted-foreground">{t.progress_percent}%</span>
                  </div>
                  <div className="h-2 overflow-hidden rounded-full bg-muted">
                    <div
                      className="h-full rounded-full bg-foreground transition-all duration-500"
                      style={{ width: `${t.progress_percent}%` }}
                    />
                  </div>
                  {role === "doctor" && (
                    <div className="flex items-center gap-2 pt-1">
                      <Input
                        type="range"
                        min="0"
                        max="100"
                        step="5"
                        defaultValue={t.progress_percent}
                        className="h-2 cursor-pointer"
                        onMouseUp={(e) => updateProgress.mutate({ tId: t.id, progress: Number((e.target as HTMLInputElement).value) })}
                      />
                    </div>
                  )}
                </div>
              )) ?? <p className="text-sm text-muted-foreground">No active treatments</p>}
            </div>
          </section>

          <section>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xs font-semibold tracking-widest uppercase text-muted-foreground">Recent Activity</h2>
            </div>
            <div className="space-y-4">
              {journey?.recent_appointments?.slice(0, 3).map((appt) => (
                <div key={appt.id} className="text-sm pb-4 border-b border-border/50 last:border-0">
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-medium text-foreground">
                      {new Date(appt.scheduled_at).toLocaleDateString("en-IN", {
                        month: "short",
                        day: "numeric",
                        year: "numeric"
                      })}
                    </span>
                    <StatusBadge status={appt.status} />
                  </div>
                  <p className="text-xs text-muted-foreground">Dr. {appt.doctor_name ?? "Care team"}</p>
                </div>
              )) ?? <p className="text-sm text-muted-foreground">No recent appointments</p>}
            </div>
          </section>
          
          <section>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xs font-semibold tracking-widest uppercase text-muted-foreground">Clinical Notes</h2>
            </div>
            <div className="space-y-3 mb-6">
              {notes?.results?.slice(0, 3).map((n) => (
                <div key={n.id} className="rounded-lg bg-muted/30 p-3 text-sm">
                  <p className="text-xs text-muted-foreground mb-1">{n.visit_date}</p>
                  <p className="text-foreground leading-relaxed whitespace-pre-wrap">{n.content}</p>
                </div>
              )) ?? <p className="text-sm text-muted-foreground">No recent notes</p>}
            </div>
            {role === "doctor" && (
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  if (!noteContent.trim()) return;
                  addNote.mutate({ patient_id: id!, content: noteContent, visit_date: noteDate });
                }}
                className="space-y-3 rounded-xl border border-border/50 bg-card/20 p-4"
              >
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label className="text-xs text-muted-foreground mb-1 block">New note</Label>
                    <Textarea
                      value={noteContent}
                      onChange={(e) => setNoteContent(e.target.value)}
                      placeholder="Document clinical observations..."
                      className="min-h-[80px] text-sm"
                      required
                    />
                  </div>
                  <div>
                    <Label className="text-xs text-muted-foreground mb-1 block">Visit Date</Label>
                    <Input
                      type="date"
                      value={noteDate}
                      onChange={(e) => setNoteDate(e.target.value)}
                      className="text-sm"
                      required
                    />
                  </div>
                </div>
                <div className="flex justify-end">
                  <Button type="submit" size="sm" disabled={addNote.isPending || !noteContent.trim()}>
                    {addNote.isPending ? "Saving..." : "Add note"}
                  </Button>
                </div>
              </form>
            )}
          </section>
        </div>
      </div>
    </motion.div>
  );
}
