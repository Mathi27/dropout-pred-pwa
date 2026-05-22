import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { Activity, BarChart3, HeartPulse, TrendingDown } from "lucide-react";

import { analyticsApi } from "@/api/analytics";
import { aiPredictionsApi } from "@/api/ai-predictions";
import { AttendanceHeatmap } from "@/components/charts/attendance-heatmap";
import { ConfidenceDistributionChart } from "@/components/charts/confidence-distribution-chart";
import { DeliveryStatusChart } from "@/components/charts/delivery-status-chart";
import { NotificationTypeChart } from "@/components/charts/notification-type-chart";
import { RiskDistributionChart } from "@/components/charts/risk-distribution-chart";
import { RiskTrendChart } from "@/components/charts/risk-trend-chart";
import { SegmentationChart } from "@/components/charts/segmentation-chart";
import { TreatmentFunnelChart } from "@/components/charts/treatment-funnel-chart";
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
import { StatCard } from "@/components/shared/stat-card";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

export function ExecutiveAnalyticsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["admin-analytics"],
    queryFn: () => analyticsApi.admin().then((r) => r.data),
  });

  const { data: riskTrends, isLoading: trendsLoading } = useQuery({
    queryKey: ["ai-risk-trends", "executive"],
    queryFn: () => aiPredictionsApi.riskTrends(30).then((r) => r.data),
  });

  const { data: overview, isLoading: overviewLoading } = useQuery({
    queryKey: ["ai-overview", "executive"],
    queryFn: () => aiPredictionsApi.overview(30).then((r) => r.data),
  });

  if (isLoading) {
    return <PageSkeleton cards={4} rows={3} />;
  }

  const adherence = data?.adherence_kpis;
  const dropout = data?.dropout_metrics;
  const intervention = data?.intervention_success;
  const riskSegmentation = data?.risk_segmentation ?? { low: 0, medium: 0, high: 0 };

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-8">
      <PageHeader
        title="Executive analytics"
        description="Operational intelligence across adherence, risk, and care delivery"
        titleClassName="font-display text-4xl"
      />

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="Attendance rate"
          value={adherence ? `${adherence.attendance_rate}%` : "—"}
          icon={Activity}
          index={0}
        />
        <StatCard
          label="Treatment completion"
          value={adherence ? `${adherence.treatment_completion_rate}%` : "—"}
          icon={HeartPulse}
          index={1}
        />
        <StatCard
          label="Payment on time"
          value={adherence ? `${adherence.payment_on_time_rate}%` : "—"}
          icon={BarChart3}
          index={2}
        />
        <StatCard
          label="High-risk share"
          value={dropout ? `${dropout.high_risk_share}%` : "—"}
          icon={TrendingDown}
          index={3}
          trend={dropout ? `${dropout.share_delta >= 0 ? "+" : ""}${dropout.share_delta}% vs prev` : undefined}
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-12">
        <Card className="lg:col-span-5">
          <CardHeader>
            <CardTitle className="text-lg">Risk distribution</CardTitle>
            <CardDescription>Latest predicted risk tiers</CardDescription>
          </CardHeader>
          <CardContent>
            <RiskDistributionChart data={riskSegmentation} />
          </CardContent>
        </Card>

        <Card className="lg:col-span-7">
          <CardHeader>
            <CardTitle className="text-lg">Risk trends</CardTitle>
            <CardDescription>30-day risk movement snapshot</CardDescription>
          </CardHeader>
          <CardContent>
            {trendsLoading ? (
              <Skeleton className="h-[260px] w-full rounded-2xl" />
            ) : riskTrends?.length ? (
              <RiskTrendChart data={riskTrends} />
            ) : (
              <EmptyState icon={TrendingDown} title="No trend data" description="Run predictions to see risk movement." />
            )}
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-12">
        <Card className="lg:col-span-4">
          <CardHeader>
            <CardTitle className="text-lg">Treatment funnel</CardTitle>
            <CardDescription>Active vs completed treatments</CardDescription>
          </CardHeader>
          <CardContent>
            <TreatmentFunnelChart
              data={
                data?.treatment_funnel ?? {
                  total: 0,
                  active: 0,
                  on_hold: 0,
                  completed: 0,
                  cancelled: 0,
                }
              }
            />
          </CardContent>
        </Card>

        <Card className="lg:col-span-4">
          <CardHeader>
            <CardTitle className="text-lg">Cohort comparison</CardTitle>
            <CardDescription>Risk by treatment category</CardDescription>
          </CardHeader>
          <CardContent>
            <SegmentationChart data={data?.cohort_comparison ?? []} />
          </CardContent>
        </Card>

        <Card className="lg:col-span-4">
          <CardHeader>
            <CardTitle className="text-lg">Delivery performance</CardTitle>
            <CardDescription>Intervention delivery mix</CardDescription>
          </CardHeader>
          <CardContent>
            <DeliveryStatusChart data={intervention?.delivery_status_counts ?? []} />
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-12">
        <Card className="lg:col-span-7">
          <CardHeader>
            <CardTitle className="text-lg">Attendance heatmap</CardTitle>
            <CardDescription>Present, absent, pending last 7 days</CardDescription>
          </CardHeader>
          <CardContent>
            <AttendanceHeatmap data={data?.attendance_heatmap ?? []} />
          </CardContent>
        </Card>

        <Card className="lg:col-span-5">
          <CardHeader>
            <CardTitle className="text-lg">Communication effectiveness</CardTitle>
            <CardDescription>Notification volume by type</CardDescription>
          </CardHeader>
          <CardContent>
            <NotificationTypeChart data={data?.communication_effectiveness?.notification_by_type ?? []} />
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-12">
        <Card className="lg:col-span-6">
          <CardHeader>
            <CardTitle className="text-lg">Intervention impact</CardTitle>
            <CardDescription>Risk movement after communication</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center justify-between rounded-xl border border-border/50 bg-card/70 p-3 text-sm">
              <span className="text-muted-foreground">Improved</span>
              <span className="font-semibold">{intervention?.impact.improved ?? 0}</span>
            </div>
            <div className="flex items-center justify-between rounded-xl border border-border/50 bg-card/70 p-3 text-sm">
              <span className="text-muted-foreground">Stable</span>
              <span className="font-semibold">{intervention?.impact.stable ?? 0}</span>
            </div>
            <div className="flex items-center justify-between rounded-xl border border-border/50 bg-card/70 p-3 text-sm">
              <span className="text-muted-foreground">Worsened</span>
              <span className="font-semibold">{intervention?.impact.worsened ?? 0}</span>
            </div>
            <div className="mt-4 grid grid-cols-2 gap-3">
              <div className="rounded-xl border border-border/50 bg-card/70 p-3 text-sm">
                <p className="text-xs text-muted-foreground">Delivery success</p>
                <p className="mt-1 text-lg font-semibold">{intervention?.delivery_success_rate ?? 0}%</p>
              </div>
              <div className="rounded-xl border border-border/50 bg-card/70 p-3 text-sm">
                <p className="text-xs text-muted-foreground">Retry rate</p>
                <p className="mt-1 text-lg font-semibold">{intervention?.retry_rate ?? 0}%</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="lg:col-span-6">
          <CardHeader>
            <CardTitle className="text-lg">Prediction confidence</CardTitle>
            <CardDescription>Distribution of model confidence tiers</CardDescription>
          </CardHeader>
          <CardContent>
            {overviewLoading ? (
              <Skeleton className="h-[240px] w-full rounded-2xl" />
            ) : (
              <ConfidenceDistributionChart
                data={
                  overview?.confidence_distribution ?? {
                    low: 0,
                    medium: 0,
                    high: 0,
                  }
                }
              />
            )}
          </CardContent>
        </Card>
      </div>

      <Card className="">
        <CardHeader>
          <CardTitle className="text-lg">Doctor performance</CardTitle>
          <CardDescription>Completion rates and high-risk load</CardDescription>
        </CardHeader>
        <CardContent>
          {data?.doctor_performance?.length ? (
            <DataTable>
              <table className="min-w-full text-left">
                <DataTableHeader>
                  <tr>
                    <DataTableHead>Doctor</DataTableHead>
                    <DataTableHead>Appointments</DataTableHead>
                    <DataTableHead>Completion</DataTableHead>
                    <DataTableHead>Patients</DataTableHead>
                    <DataTableHead>High risk</DataTableHead>
                  </tr>
                </DataTableHeader>
                <DataTableBody>
                  {data.doctor_performance.map((row) => (
                    <DataTableRow key={row.doctor_id}>
                      <DataTableCell className="font-medium">{row.doctor_name}</DataTableCell>
                      <DataTableCell>{row.appointments_total}</DataTableCell>
                      <DataTableCell>{row.completion_rate}%</DataTableCell>
                      <DataTableCell>{row.patients_seen}</DataTableCell>
                      <DataTableCell>{row.high_risk_patients}</DataTableCell>
                    </DataTableRow>
                  ))}
                </DataTableBody>
              </table>
            </DataTable>
          ) : (
            <p className="text-sm text-muted-foreground">No doctor analytics yet.</p>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}
