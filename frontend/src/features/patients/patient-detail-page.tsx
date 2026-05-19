import { useMutation, useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { useParams } from "react-router-dom";

import { aiPredictionsApi } from "@/api/ai-predictions";
import { patientsApi } from "@/api/patients";
import { clinicalNotesApi, patientTreatmentsApi } from "@/api/resources";
import { PageHeader } from "@/components/shared/page-header";
import { PatientRiskTimeline } from "@/components/shared/patient-risk-timeline";
import { PredictionHistoryTimeline } from "@/components/shared/prediction-history-timeline";
import { RiskBadge } from "@/components/shared/risk-badge";
import { ShapExplanationCard } from "@/components/shared/shap-explanation-card";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";

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

  const { data: timeline, refetch: refetchTimeline } = useQuery({
    queryKey: ["ai-timeline", id],
    queryFn: () => aiPredictionsApi.timeline(id!, 120).then((r) => r.data),
    enabled: !!id,
  });

  const { mutateAsync: runPrediction, isPending } = useMutation({
    mutationFn: () => aiPredictionsApi.generate(id!).then((r) => r.data),
    onSuccess: () => {
      refetchPrediction();
      refetchExplanation();
      refetchHistory();
      refetchTimeline();
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

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="glass-card border-0 shadow-card">
          <CardHeader>
            <CardTitle>Risk overview</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <RiskBadge
              score={prediction?.risk_score ?? patient.risk_score}
              level={prediction?.risk_level ?? patient.risk_level}
              className="text-sm"
            />
            <div className="rounded-xl border border-border/50 bg-muted/30 p-4">
              <p className="text-xs uppercase tracking-wider text-muted-foreground">Probability</p>
              <p className="mt-2 text-2xl font-semibold">
                {prediction ? `${Math.round(prediction.probability * 100)}%` : "—"}
              </p>
              <p className="mt-2 text-xs text-muted-foreground">
                Based on visits, treatments, payments, and engagement
              </p>
            </div>
          </CardContent>
        </Card>

        <ShapExplanationCard explanation={explanation} />

        <Card className="glass-card border-0 shadow-card">
          <CardHeader>
            <CardTitle>Prediction history</CardTitle>
          </CardHeader>
          <CardContent>
            <PredictionHistoryTimeline predictions={history ?? []} />
          </CardContent>
        </Card>
      </div>

      <Card className="glass-card border-0 shadow-card">
        <CardHeader>
          <CardTitle>Patient risk timeline</CardTitle>
        </CardHeader>
        <CardContent>
          <PatientRiskTimeline events={timeline?.events ?? []} />
        </CardContent>
      </Card>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card className="glass-card border-0 shadow-card">
          <CardHeader>
            <CardTitle>Treatments</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {treatments?.results?.map((t) => (
              <div key={t.id}>
                <div className="mb-1 flex justify-between text-sm">
                  <span>{t.treatment_detail?.name}</span>
                  <span>{t.progress_percent}%</span>
                </div>
                <div className="h-2 overflow-hidden rounded-full bg-muted">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${t.progress_percent}%` }}
                    className="h-full rounded-full bg-gradient-to-r from-primary to-teal-400"
                  />
                </div>
              </div>
            )) ?? <p className="text-sm text-muted-foreground">No treatments</p>}
          </CardContent>
        </Card>

        <Card className="glass-card border-0 shadow-card">
          <CardHeader>
            <CardTitle>Clinical notes</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {notes?.results?.map((n) => (
              <div key={n.id} className="rounded-lg border p-3 text-sm">
                <p className="text-xs text-muted-foreground">{n.visit_date}</p>
                <p className="mt-1">{n.content}</p>
              </div>
            )) ?? <p className="text-sm text-muted-foreground">No notes yet</p>}
          </CardContent>
        </Card>
      </div>
    </motion.div>
  );
}
