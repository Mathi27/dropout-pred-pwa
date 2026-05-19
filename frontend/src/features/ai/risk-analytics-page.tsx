import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { Activity, Brain, Gauge, TrendingUp, Users } from "lucide-react";
import { Link } from "react-router-dom";

import { aiPredictionsApi } from "@/api/ai-predictions";
import { AdherenceHeatmap } from "@/components/charts/adherence-heatmap";
import { CompletionTrendChart } from "@/components/charts/completion-trend-chart";
import { ConfidenceDistributionChart } from "@/components/charts/confidence-distribution-chart";
import { NotificationEffectivenessChart } from "@/components/charts/notification-effectiveness-chart";
import { RiskDistributionChart } from "@/components/charts/risk-distribution-chart";
import { RiskTrendChart } from "@/components/charts/risk-trend-chart";
import { SegmentationChart } from "@/components/charts/segmentation-chart";
import {
  DataTable,
  DataTableBody,
  DataTableCell,
  DataTableHead,
  DataTableHeader,
  DataTableRow,
} from "@/components/shared/data-table";
import { EmptyState } from "@/components/shared/empty-state";
import { PageHeader } from "@/components/shared/page-header";
import { PageSkeleton } from "@/components/shared/page-skeleton";
import { RiskActivityTimeline } from "@/components/shared/risk-activity-timeline";
import { RiskBadge } from "@/components/shared/risk-badge";
import { StatCard } from "@/components/shared/stat-card";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import type { RiskTrendPoint } from "@/types/api";

export function RiskAnalyticsPage() {
  const {
    data: metrics,
    isLoading: metricsLoading,
    isError: metricsError,
  } = useQuery({
    queryKey: ["ai-metrics"],
    queryFn: () => aiPredictionsApi.metrics().then((r) => r.data),
    retry: false,
  });

  const {
    data: trends,
    isLoading: trendsLoading,
  } = useQuery({
    queryKey: ["ai-risk-trends"],
    queryFn: () => aiPredictionsApi.riskTrends(30).then((r) => r.data),
  });

  const {
    data: overview,
    isLoading: overviewLoading,
  } = useQuery({
    queryKey: ["ai-overview"],
    queryFn: () => aiPredictionsApi.overview(30).then((r) => r.data),
  });

  const {
    data: highRisk,
    isLoading: highRiskLoading,
  } = useQuery({
    queryKey: ["ai-high-risk"],
    queryFn: () => aiPredictionsApi.highRisk().then((r) => r.data),
  });

  const trendSeries = trends ?? [];
  const totalCounts = trendSeries.reduce(
    (acc, day) => {
      acc.low += day.low;
      acc.medium += day.medium;
      acc.high += day.high;
      acc.total += day.total;
      return acc;
    },
    { low: 0, medium: 0, high: 0, total: 0 },
  );
  const riskDistribution = overview?.risk_distribution ?? {
    low: totalCounts.low,
    medium: totalCounts.medium,
    high: totalCounts.high,
  };
  const totalPredictions = riskDistribution.low + riskDistribution.medium + riskDistribution.high;
  const highShare = totalPredictions ? riskDistribution.high / totalPredictions : 0;
  const stableShare = totalPredictions
    ? (riskDistribution.low + riskDistribution.medium) / totalPredictions
    : 0;

  const trendCounts = overview?.risk_trends ?? { rising: 0, falling: 0, stable: 0 };
  const confidenceDistribution = overview?.confidence_distribution ?? { low: 0, medium: 0, high: 0 };
  const completionTrend = overview?.completion_trend ?? [];
  const adherenceHeatmap = overview?.adherence_heatmap ?? [];
  const segmentation = overview?.segmentation ?? [];
  const interventionImpact = overview?.intervention_impact ?? { improved: 0, worsened: 0, stable: 0 };
  const notificationEffectiveness = overview?.notification_effectiveness ?? {};
  const notificationData = [
    { risk: "Low", read_rate: notificationEffectiveness.low?.read_rate ?? 0 },
    { risk: "Medium", read_rate: notificationEffectiveness.medium?.read_rate ?? 0 },
    { risk: "High", read_rate: notificationEffectiveness.high?.read_rate ?? 0 },
  ];

  const recentWindow = trendSeries.slice(-7);
  const previousWindow = trendSeries.slice(-14, -7);
  const sumWindow = (items: RiskTrendPoint[], key: "low" | "medium" | "high") =>
    items.reduce((sum, item) => sum + item[key], 0);
  const recentHigh = sumWindow(recentWindow, "high");
  const previousHigh = sumWindow(previousWindow, "high");
  const recentStable = sumWindow(recentWindow, "low") + sumWindow(recentWindow, "medium");
  const previousStable = sumWindow(previousWindow, "low") + sumWindow(previousWindow, "medium");
  const highDelta = recentHigh - previousHigh;
  const stableDelta = recentStable - previousStable;

  const recentHighRisk = (highRisk ?? [])
    .slice()
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, 6);

  const aucValue = metrics?.metrics?.auc;
  const trainedAt = metrics?.model_version?.trained_at
    ? new Date(metrics.model_version.trained_at).toLocaleDateString("en-IN", {
        dateStyle: "medium",
      })
    : "—";

  if (metricsLoading) {
    return <PageSkeleton cards={4} rows={4} />;
  }

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-8">
      <PageHeader
        title="AI risk intelligence"
        description="Dropout risk, adherence signals, and model performance"
        titleClassName="font-display text-4xl"
        descriptionClassName="max-w-xl"
      >
        <Button variant="outline" asChild className="rounded-xl">
          <Link to="/patients">Review patients</Link>
        </Button>
      </PageHeader>

      <div className="grid gap-6 lg:grid-cols-12">
        <Card className="glass-card hero-gradient border-0 lg:col-span-5">
          <CardHeader>
            <CardTitle className="text-lg font-display">AI model health</CardTitle>
            <CardDescription>Champion model calibration and performance</CardDescription>
          </CardHeader>
          <CardContent className="space-y-5">
            {metricsError ? (
              <div className="rounded-2xl border border-dashed border-border/60 bg-card/70 p-4 text-sm text-muted-foreground">
                Train a model to unlock AI insights.
              </div>
            ) : (
              <>
                <div className="flex items-end justify-between gap-4">
                  <div>
                    <p className="text-xs uppercase tracking-wider text-muted-foreground">AUC</p>
                    <p className="mt-2 text-4xl font-display font-semibold text-foreground">
                      {aucValue !== undefined ? aucValue.toFixed(3) : "—"}
                    </p>
                    <p className="mt-1 text-xs text-muted-foreground">Calibration stable</p>
                  </div>
                  <div className="rounded-2xl border border-border/60 bg-card/70 p-3 text-xs">
                    <p className="text-muted-foreground">Active model</p>
                    <p className="mt-1 font-semibold text-foreground">
                      {metrics?.model_version?.name ?? "—"}
                    </p>
                    <p className="mt-1 text-muted-foreground">Trained {trainedAt}</p>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div className="rounded-xl border border-border/60 bg-card/70 p-3">
                    <p className="text-xs text-muted-foreground">Precision</p>
                    <p className="mt-1 text-lg font-semibold">
                      {metrics?.metrics?.precision?.toFixed(2) ?? "—"}
                    </p>
                  </div>
                  <div className="rounded-xl border border-border/60 bg-card/70 p-3">
                    <p className="text-xs text-muted-foreground">Recall</p>
                    <p className="mt-1 text-lg font-semibold">
                      {metrics?.metrics?.recall?.toFixed(2) ?? "—"}
                    </p>
                  </div>
                  <div className="rounded-xl border border-border/60 bg-card/70 p-3">
                    <p className="text-xs text-muted-foreground">F1 score</p>
                    <p className="mt-1 text-lg font-semibold">
                      {metrics?.metrics?.f1?.toFixed(2) ?? "—"}
                    </p>
                  </div>
                  <div className="rounded-xl border border-border/60 bg-card/70 p-3">
                    <p className="text-xs text-muted-foreground">Brier</p>
                    <p className="mt-1 text-lg font-semibold">
                      {metrics?.metrics?.brier?.toFixed(3) ?? "—"}
                    </p>
                  </div>
                </div>
              </>
            )}
          </CardContent>
        </Card>

        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4 lg:col-span-7">
          <StatCard
            label="Active model"
            value={metrics?.model_version?.name ?? "—"}
            icon={Brain}
            index={0}
            loading={metricsLoading}
          />
          <StatCard
            label="High-risk patients"
            value={highRisk?.length ?? 0}
            icon={Activity}
            index={1}
            loading={highRiskLoading}
          />
          <StatCard
            label="30-day predictions"
            value={totalPredictions}
            icon={Users}
            index={2}
            loading={trendsLoading}
          />
          <StatCard
            label="High-risk share"
            value={totalPredictions ? `${(highShare * 100).toFixed(1)}%` : "—"}
            icon={Gauge}
            index={3}
            loading={trendsLoading}
          />
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-12">
        <Card className="glass-card border-0 lg:col-span-7">
          <CardHeader>
            <CardTitle className="text-lg">Risk trends</CardTitle>
            <CardDescription>Low, medium, and high risk over the last 30 days</CardDescription>
          </CardHeader>
          <CardContent>
            {trendsLoading ? (
              <Skeleton className="h-[300px] w-full rounded-2xl" />
            ) : trendSeries.length ? (
              <RiskTrendChart data={trendSeries} />
            ) : (
              <EmptyState
                icon={TrendingUp}
                title="No trend data"
                description="Run predictions to unlock risk movement analytics."
              />
            )}
          </CardContent>
        </Card>

        <div className="grid gap-6 lg:col-span-5">
          <Card className="glass-card border-0">
            <CardHeader>
              <CardTitle className="text-lg">Risk distribution</CardTitle>
              <CardDescription>Share of predictions by risk tier</CardDescription>
            </CardHeader>
            <CardContent>
              {trendsLoading ? (
                <Skeleton className="h-[240px] w-full rounded-2xl" />
              ) : (
                <>
                  <RiskDistributionChart
                    data={{
                      low: riskDistribution.low,
                      medium: riskDistribution.medium,
                      high: riskDistribution.high,
                    }}
                  />
                  {totalPredictions ? (
                    <div className="mt-4 grid grid-cols-3 gap-2 text-xs">
                      <div className="rounded-xl border border-border/50 p-2 text-center">
                        <p className="text-muted-foreground">Low</p>
                        <p className="mt-1 font-semibold">{Math.round((riskDistribution.low / totalPredictions) * 100)}%</p>
                      </div>
                      <div className="rounded-xl border border-border/50 p-2 text-center">
                        <p className="text-muted-foreground">Medium</p>
                        <p className="mt-1 font-semibold">{Math.round((riskDistribution.medium / totalPredictions) * 100)}%</p>
                      </div>
                      <div className="rounded-xl border border-border/50 p-2 text-center">
                        <p className="text-muted-foreground">High</p>
                        <p className="mt-1 font-semibold">{Math.round((riskDistribution.high / totalPredictions) * 100)}%</p>
                      </div>
                    </div>
                  ) : null}
                </>
              )}
            </CardContent>
          </Card>

          <Card className="glass-card border-0">
            <CardHeader>
              <CardTitle className="text-lg">Cohort comparison</CardTitle>
              <CardDescription>High-risk vs stable engagement cohorts</CardDescription>
            </CardHeader>
            <CardContent>
              {!totalPredictions ? (
                <EmptyState
                  icon={Activity}
                  title="No cohort data"
                  description="Generate predictions to compare risk cohorts."
                />
              ) : (
                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="rounded-2xl border border-border/60 bg-card/80 p-4">
                    <p className="text-xs uppercase tracking-wider text-muted-foreground">High risk</p>
                    <p className="mt-2 text-2xl font-semibold">{totalCounts.high}</p>
                    <p className="text-xs text-muted-foreground">
                      {(highShare * 100).toFixed(1)}% of predictions
                    </p>
                    <div className="mt-3 h-2 rounded-full bg-muted">
                      <div
                        className="h-2 rounded-full"
                        style={{ width: `${highShare * 100}%`, background: "hsl(var(--risk-high))" }}
                      />
                    </div>
                    <p className="mt-2 text-xs text-muted-foreground">
                      {highDelta >= 0 ? "+" : ""}{highDelta} vs previous 7d
                    </p>
                  </div>
                  <div className="rounded-2xl border border-border/60 bg-card/80 p-4">
                    <p className="text-xs uppercase tracking-wider text-muted-foreground">Stable cohort</p>
                    <p className="mt-2 text-2xl font-semibold">{totalCounts.low + totalCounts.medium}</p>
                    <p className="text-xs text-muted-foreground">
                      {(stableShare * 100).toFixed(1)}% of predictions
                    </p>
                    <div className="mt-3 h-2 rounded-full bg-muted">
                      <div
                        className="h-2 rounded-full"
                        style={{ width: `${stableShare * 100}%`, background: "hsl(var(--risk-low))" }}
                      />
                    </div>
                    <p className="mt-2 text-xs text-muted-foreground">
                      {stableDelta >= 0 ? "+" : ""}{stableDelta} vs previous 7d
                    </p>
                  </div>
                  <div className="rounded-2xl border border-border/60 bg-card/80 p-4">
                    <p className="text-xs uppercase tracking-wider text-muted-foreground">Risk shifts</p>
                    <div className="mt-3 space-y-2 text-sm">
                      <div className="flex items-center justify-between">
                        <span className="text-muted-foreground">Rising</span>
                        <span className="font-semibold text-rose-600 dark:text-rose-400">{trendCounts.rising}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-muted-foreground">Falling</span>
                        <span className="font-semibold text-emerald-600 dark:text-emerald-400">{trendCounts.falling}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-muted-foreground">Stable</span>
                        <span className="font-semibold">{trendCounts.stable}</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-12">
        <Card className="glass-card border-0 lg:col-span-6">
          <CardHeader>
            <CardTitle className="text-lg">Treatment completion trends</CardTitle>
            <CardDescription>Average completion progression (12 weeks)</CardDescription>
          </CardHeader>
          <CardContent>
            {overviewLoading ? (
              <Skeleton className="h-[240px] w-full rounded-2xl" />
            ) : completionTrend.length ? (
              <CompletionTrendChart data={completionTrend} />
            ) : (
              <EmptyState
                icon={TrendingUp}
                title="No completion data"
                description="Treatments will populate completion trends soon."
              />
            )}
          </CardContent>
        </Card>

        <Card className="glass-card border-0 lg:col-span-3">
          <CardHeader>
            <CardTitle className="text-lg">Adherence heatmap</CardTitle>
            <CardDescription>Miss rate by weekday</CardDescription>
          </CardHeader>
          <CardContent>
            {overviewLoading ? (
              <Skeleton className="h-[220px] w-full rounded-2xl" />
            ) : adherenceHeatmap.length ? (
              <AdherenceHeatmap data={adherenceHeatmap} />
            ) : (
              <EmptyState
                icon={Activity}
                title="No adherence data"
                description="Appointment attendance will appear here."
              />
            )}
          </CardContent>
        </Card>

        <Card className="glass-card border-0 lg:col-span-3">
          <CardHeader>
            <CardTitle className="text-lg">Prediction confidence</CardTitle>
            <CardDescription>Model certainty distribution</CardDescription>
          </CardHeader>
          <CardContent>
            {overviewLoading ? (
              <Skeleton className="h-[220px] w-full rounded-2xl" />
            ) : (
              <ConfidenceDistributionChart data={confidenceDistribution} />
            )}
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-12">
        <Card className="glass-card border-0 lg:col-span-7">
          <CardHeader>
            <CardTitle className="text-lg">Patient segmentation</CardTitle>
            <CardDescription>Risk mix by primary treatment category</CardDescription>
          </CardHeader>
          <CardContent>
            {overviewLoading ? (
              <Skeleton className="h-[260px] w-full rounded-2xl" />
            ) : segmentation.length ? (
              <SegmentationChart data={segmentation} />
            ) : (
              <EmptyState
                icon={Users}
                title="No segmentation data"
                description="Segmentation appears once treatments and predictions exist."
              />
            )}
          </CardContent>
        </Card>

        <div className="grid gap-6 lg:col-span-5">
          <Card className="glass-card border-0">
            <CardHeader>
              <CardTitle className="text-lg">Notification effectiveness</CardTitle>
              <CardDescription>Read rate by risk cohort</CardDescription>
            </CardHeader>
            <CardContent>
              {overviewLoading ? (
                <Skeleton className="h-[220px] w-full rounded-2xl" />
              ) : (
                <NotificationEffectivenessChart data={notificationData} />
              )}
            </CardContent>
          </Card>

          <Card className="glass-card border-0">
            <CardHeader>
              <CardTitle className="text-lg">Intervention impact</CardTitle>
              <CardDescription>Risk movement after recent outreach</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-3 gap-3 text-center text-sm">
                <div className="rounded-xl border border-border/60 bg-card/80 p-3">
                  <p className="text-xs text-muted-foreground">Improved</p>
                  <p className="mt-2 text-lg font-semibold text-emerald-600 dark:text-emerald-400">
                    {interventionImpact.improved}
                  </p>
                </div>
                <div className="rounded-xl border border-border/60 bg-card/80 p-3">
                  <p className="text-xs text-muted-foreground">Stable</p>
                  <p className="mt-2 text-lg font-semibold">{interventionImpact.stable}</p>
                </div>
                <div className="rounded-xl border border-border/60 bg-card/80 p-3">
                  <p className="text-xs text-muted-foreground">Worsened</p>
                  <p className="mt-2 text-lg font-semibold text-rose-600 dark:text-rose-400">
                    {interventionImpact.worsened}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-12">
        <Card className="glass-card border-0 lg:col-span-7">
          <CardHeader>
            <CardTitle className="text-lg">High-risk patients</CardTitle>
            <CardDescription>Prioritize outreach for likely dropouts</CardDescription>
          </CardHeader>
          <CardContent>
            {highRiskLoading ? (
              <Skeleton className="h-[260px] w-full rounded-2xl" />
            ) : !highRisk?.length ? (
              <EmptyState
                icon={Users}
                title="No high-risk patients"
                description="Model predictions will appear here."
              />
            ) : (
              <DataTable>
                <table className="w-full min-w-[640px]">
                  <DataTableHeader>
                    <DataTableHead>Patient</DataTableHead>
                    <DataTableHead>Email</DataTableHead>
                    <DataTableHead>Risk</DataTableHead>
                    <DataTableHead className="text-right">Action</DataTableHead>
                  </DataTableHeader>
                  <DataTableBody>
                    {highRisk.map((p) => {
                      const score = p.risk_score ?? Math.round(p.probability * 100);
                      return (
                        <DataTableRow key={p.id}>
                          <DataTableCell>{p.patient_detail?.full_name ?? "Patient"}</DataTableCell>
                          <DataTableCell className="text-muted-foreground">
                            {p.patient_detail?.email ?? "—"}
                          </DataTableCell>
                          <DataTableCell>
                            <RiskBadge score={score} level={p.risk_level} />
                          </DataTableCell>
                          <DataTableCell className="text-right">
                            {p.patient_detail?.id ? (
                              <Button variant="ghost" size="sm" asChild className="rounded-lg">
                                <Link to={`/patients/${p.patient_detail.id}`}>View</Link>
                              </Button>
                            ) : (
                              <span className="text-xs text-muted-foreground">—</span>
                            )}
                          </DataTableCell>
                        </DataTableRow>
                      );
                    })}
                  </DataTableBody>
                </table>
              </DataTable>
            )}
          </CardContent>
        </Card>

        <Card className="glass-card border-0 lg:col-span-5">
          <CardHeader>
            <CardTitle className="text-lg">Patient risk timeline</CardTitle>
            <CardDescription>Most recent high-risk signals</CardDescription>
          </CardHeader>
          <CardContent>
            {highRiskLoading ? (
              <Skeleton className="h-[260px] w-full rounded-2xl" />
            ) : (
              <RiskActivityTimeline predictions={recentHighRisk} />
            )}
          </CardContent>
        </Card>
      </div>
    </motion.div>
  );
}
