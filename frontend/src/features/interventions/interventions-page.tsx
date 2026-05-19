import { useMemo, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { MessageSquare, Send, Shield, Sparkles, Users } from "lucide-react";

import { aiInterventionsApi } from "@/api/ai-interventions";
import { aiPredictionsApi } from "@/api/ai-predictions";
import { DeliveryStatusChart } from "@/components/charts/delivery-status-chart";
import { LanguageEngagementChart } from "@/components/charts/language-engagement-chart";
import { CommunicationTimeline } from "@/components/shared/communication-timeline";
import { DeliveryStatusBadge } from "@/components/shared/delivery-status-badge";
import { EmptyState } from "@/components/shared/empty-state";
import { PageHeader } from "@/components/shared/page-header";
import { PageSkeleton } from "@/components/shared/page-skeleton";
import { RiskBadge } from "@/components/shared/risk-badge";
import { StatCard } from "@/components/shared/stat-card";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useAuthStore } from "@/stores/auth-store";
import type { AIGeneratedMessage } from "@/types/api";

const MESSAGE_TYPES = [
  { value: "appointment_reminder", label: "Appointment reminder" },
  { value: "missed_followup", label: "Missed follow-up" },
  { value: "treatment_encouragement", label: "Treatment encouragement" },
  { value: "motivational", label: "Motivational reminder" },
  { value: "educational", label: "Educational tip" },
];

const LANGUAGE_OPTIONS = [
  { value: "en", label: "English" },
  { value: "ta", label: "Tamil" },
  { value: "hi", label: "Hindi" },
  { value: "te", label: "Telugu" },
];

export function InterventionsPage() {
  const role = useAuthStore((state) => state.user?.role);
  const isAdmin = role === "admin";

  const [selectedPatientId, setSelectedPatientId] = useState<string | null>(null);
  const [messageType, setMessageType] = useState<string>("");
  const [language, setLanguage] = useState<string>("");
  const [previewMessage, setPreviewMessage] = useState<AIGeneratedMessage | null>(null);

  const { data: highRisk, isLoading: highRiskLoading } = useQuery({
    queryKey: ["ai-interventions-high-risk"],
    queryFn: () => aiPredictionsApi.highRisk().then((r) => r.data),
  });

  const { data: patientHistory, isLoading: historyLoading, refetch: refetchHistory } = useQuery({
    queryKey: ["ai-interventions-history", selectedPatientId],
    queryFn: () => aiInterventionsApi.patientHistory(selectedPatientId!, 15).then((r) => r.data),
    enabled: !!selectedPatientId,
  });

  const {
    data: metrics,
    isLoading: metricsLoading,
    isError: metricsError,
  } = useQuery({
    queryKey: ["ai-interventions-metrics"],
    queryFn: () => aiInterventionsApi.metrics().then((r) => r.data),
    enabled: isAdmin,
    retry: false,
  });

  const selectedPatient = useMemo(
    () => highRisk?.find((item) => item.patient_detail?.id === selectedPatientId),
    [highRisk, selectedPatientId],
  );

  const previewMutation = useMutation({
    mutationFn: () =>
      aiInterventionsApi
        .preview({ patient_id: selectedPatientId!, message_type: messageType || undefined, language: language || undefined })
        .then((r) => r.data),
    onSuccess: (data) => {
      setPreviewMessage(data);
    },
  });

  const sendMutation = useMutation({
    mutationFn: () =>
      aiInterventionsApi
        .generate({ patient_id: selectedPatientId!, message_type: messageType || undefined, language: language || undefined })
        .then((r) => r.data),
    onSuccess: async (message) => {
      setPreviewMessage(message);
      await aiInterventionsApi.simulateDelivery(message.id);
      refetchHistory();
    },
  });

  const totals = metrics?.totals;
  const deliveryRate = totals?.messages ? (totals.delivered / totals.messages) * 100 : 0;
  const avgConfidence = metrics?.avg_confidence ? metrics.avg_confidence * 100 : 0;

  if (highRiskLoading) {
    return <PageSkeleton cards={4} rows={3} />;
  }

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-8">
      <PageHeader
        title="AI interventions"
        description="Personalized communication studio with multilingual outreach and delivery insights"
        titleClassName="font-display text-4xl"
      />

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard label="High-risk patients" value={highRisk?.length ?? 0} icon={Users} index={0} />
        <StatCard
          label="Messages sent"
          value={totals?.messages ?? "—"}
          icon={Send}
          index={1}
          loading={metricsLoading && isAdmin}
        />
        <StatCard
          label="Delivery rate"
          value={totals ? `${deliveryRate.toFixed(1)}%` : "—"}
          icon={Sparkles}
          index={2}
          loading={metricsLoading && isAdmin}
        />
        <StatCard
          label="Avg confidence"
          value={metrics ? `${avgConfidence.toFixed(0)}%` : "—"}
          icon={Shield}
          index={3}
          loading={metricsLoading && isAdmin}
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-12">
        <Card className="glass-card border-0 lg:col-span-7">
          <CardHeader>
            <CardTitle className="text-lg">Message preview studio</CardTitle>
            <CardDescription>Draft empathetic messages before triggering delivery</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {!selectedPatient ? (
              <EmptyState
                icon={MessageSquare}
                title="Select a patient"
                description="Choose a high-risk patient to generate a personalized message."
              />
            ) : (
              <div className="space-y-4">
                <div className="flex flex-wrap items-center gap-3">
                  <div className="rounded-xl border border-border/60 bg-card/70 px-3 py-2 text-sm">
                    {selectedPatient.patient_detail?.full_name}
                  </div>
                  <RiskBadge
                    score={selectedPatient.risk_score ?? Math.round(selectedPatient.probability * 100)}
                    level={selectedPatient.risk_level}
                  />
                  <DeliveryStatusBadge status={previewMessage?.delivery_status} />
                </div>

                <div className="grid gap-3 md:grid-cols-2">
                  <label className="space-y-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    Message type
                    <select
                      className="h-10 w-full rounded-xl border border-border/60 bg-background px-3 text-sm"
                      value={messageType}
                      onChange={(event) => setMessageType(event.target.value)}
                    >
                      <option value="">Smart recommendation</option>
                      {MESSAGE_TYPES.map((type) => (
                        <option key={type.value} value={type.value}>
                          {type.label}
                        </option>
                      ))}
                    </select>
                  </label>

                  <label className="space-y-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    Language
                    <select
                      className="h-10 w-full rounded-xl border border-border/60 bg-background px-3 text-sm"
                      value={language}
                      onChange={(event) => setLanguage(event.target.value)}
                    >
                      <option value="">Auto from patient</option>
                      {LANGUAGE_OPTIONS.map((option) => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                  </label>
                </div>

                <div className="rounded-2xl border border-border/60 bg-muted/30 p-4 text-sm text-foreground/90">
                  {previewMutation.isPending ? (
                    <Skeleton className="h-24 w-full" />
                  ) : previewMessage ? (
                    <p>{previewMessage.content}</p>
                  ) : (
                    <p className="text-muted-foreground">Generate a preview to view the AI draft.</p>
                  )}
                </div>

                <div className="flex flex-wrap gap-3">
                  <Button
                    variant="outline"
                    className="rounded-xl"
                    disabled={!selectedPatientId || previewMutation.isPending}
                    onClick={() => previewMutation.mutate()}
                  >
                    {previewMutation.isPending ? "Generating..." : "Preview message"}
                  </Button>
                  <Button
                    className="rounded-xl"
                    disabled={!selectedPatientId || sendMutation.isPending}
                    onClick={() => sendMutation.mutate()}
                  >
                    {sendMutation.isPending ? "Sending..." : "Send & simulate"}
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="glass-card border-0 lg:col-span-5">
          <CardHeader>
            <CardTitle className="text-lg">Communication analytics</CardTitle>
            <CardDescription>Delivery effectiveness and language reach</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {metricsError && !metricsLoading ? (
              <div className="rounded-2xl border border-dashed border-border/60 bg-card/70 p-4 text-sm text-muted-foreground">
                Admin analytics available for clinic leadership only.
              </div>
            ) : (
              <>
                <div>
                  <p className="text-xs uppercase tracking-wider text-muted-foreground">Delivery status</p>
                  {metricsLoading ? (
                    <Skeleton className="mt-3 h-[220px] w-full rounded-2xl" />
                  ) : (
                    <DeliveryStatusChart data={metrics?.status_counts ?? []} />
                  )}
                </div>
                <div>
                  <p className="text-xs uppercase tracking-wider text-muted-foreground">Language reach</p>
                  {metricsLoading ? (
                    <Skeleton className="mt-3 h-[220px] w-full rounded-2xl" />
                  ) : (
                    <LanguageEngagementChart data={metrics?.language_counts ?? []} />
                  )}
                </div>
              </>
            )}
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-12">
        <Card className="glass-card border-0 lg:col-span-7">
          <CardHeader>
            <CardTitle className="text-lg">Communication timeline</CardTitle>
            <CardDescription>Chronological interventions for the selected patient</CardDescription>
          </CardHeader>
          <CardContent>
            {historyLoading ? (
              <Skeleton className="h-[280px] w-full rounded-2xl" />
            ) : (
              <CommunicationTimeline messages={patientHistory ?? []} />
            )}
          </CardContent>
        </Card>

        <Card className="glass-card border-0 lg:col-span-5">
          <CardHeader>
            <CardTitle className="text-lg">High-risk queue</CardTitle>
            <CardDescription>Prioritize personalized outreach</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {highRisk?.length ? (
              highRisk.slice(0, 8).map((item, index) => (
                <motion.button
                  key={item.id}
                  type="button"
                  initial={{ opacity: 0, x: 8 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.03 }}
                  whileHover={{ scale: 1.01 }}
                  onClick={() => {
                    setSelectedPatientId(item.patient_detail?.id ?? null);
                    setPreviewMessage(null);
                  }}
                  className={
                    item.patient_detail?.id === selectedPatientId
                      ? "w-full rounded-2xl border border-primary/40 bg-primary/10 p-3 text-left"
                      : "w-full rounded-2xl border border-border/60 bg-card/80 p-3 text-left"
                  }
                >
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <p className="text-sm font-semibold">
                        {item.patient_detail?.full_name ?? "Patient"}
                      </p>
                      <p className="text-xs text-muted-foreground">{item.patient_detail?.email ?? ""}</p>
                    </div>
                    <RiskBadge score={item.risk_score ?? Math.round(item.probability * 100)} level={item.risk_level} />
                  </div>
                </motion.button>
              ))
            ) : (
              <EmptyState icon={Users} title="No high-risk patients" description="Generate predictions to populate the queue." />
            )}
          </CardContent>
        </Card>
      </div>
    </motion.div>
  );
}
