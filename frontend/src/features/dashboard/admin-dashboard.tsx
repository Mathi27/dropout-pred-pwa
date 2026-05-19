import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { Activity, Calendar, TrendingUp, Users } from "lucide-react";
import { Link } from "react-router-dom";
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

import { analyticsApi } from "@/api/analytics";
import { AppointmentTrendChart } from "@/components/charts/appointment-trend-chart";
import { AttendanceHeatmap } from "@/components/charts/attendance-heatmap";
import { PageHeader } from "@/components/shared/page-header";
import { PageSkeleton } from "@/components/shared/page-skeleton";
import { StatCard } from "@/components/shared/stat-card";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const PIE_COLORS = ["hsl(var(--primary))", "hsl(215 16% 65%)"];

const tooltipStyle = {
  borderRadius: "12px",
  border: "1px solid hsl(var(--border))",
  background: "hsl(var(--card))",
  fontSize: "12px",
};

export function AdminDashboard() {
  const { data, isLoading } = useQuery({
    queryKey: ["admin-analytics"],
    queryFn: () => analyticsApi.admin().then((r) => r.data),
  });

  const kpis = data?.kpis;
  const notifPie = data
    ? [
        { name: "Unread", value: data.notification_metrics.unread },
        { name: "Read", value: data.notification_metrics.read },
      ]
    : [];

  if (isLoading) {
    return <PageSkeleton cards={4} rows={0} />;
  }

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-8">
      <PageHeader title="Executive overview" description="Real-time clinic performance metrics">
        <Button variant="outline" asChild className="rounded-xl">
          <Link to="/admin/audit">Audit logs</Link>
        </Button>
      </PageHeader>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Total patients" value={kpis?.total_patients ?? "—"} icon={Users} index={0} trend="Active registry" />
        <StatCard label="Today" value={kpis?.appointments_today ?? "—"} icon={Calendar} index={1} trend="Scheduled today" />
        <StatCard label="Completion" value={`${kpis?.completion_rate ?? "—"}%`} icon={TrendingUp} index={2} />
        <StatCard label="Active treatments" value={kpis?.active_treatments ?? "—"} icon={Activity} index={3} />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="glass-card border-0 lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-lg">Appointment trends</CardTitle>
            <CardDescription>7-day scheduled vs completed volume</CardDescription>
          </CardHeader>
          <CardContent>
            <AppointmentTrendChart data={data?.appointment_trends ?? []} />
          </CardContent>
        </Card>

        <Card className="glass-card border-0">
          <CardHeader>
            <CardTitle className="text-lg">Notifications</CardTitle>
            <CardDescription>Read vs unread distribution</CardDescription>
          </CardHeader>
          <CardContent className="h-[280px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={notifPie}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={85}
                  paddingAngle={3}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  labelLine={false}
                >
                  {notifPie.map((_, i) => (
                    <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={tooltipStyle} />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <Card className="glass-card border-0">
        <CardHeader>
          <CardTitle className="text-lg">Attendance heatmap</CardTitle>
          <CardDescription>Last 7 days — present count per day</CardDescription>
        </CardHeader>
        <CardContent>
          <AttendanceHeatmap data={data?.attendance_heatmap ?? []} />
        </CardContent>
      </Card>
    </motion.div>
  );
}
