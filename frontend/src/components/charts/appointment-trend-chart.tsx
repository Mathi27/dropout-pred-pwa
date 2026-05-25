import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

interface TrendPoint {
  date: string;
  scheduled: number;
  completed: number;
}

const tooltipStyle = {
  borderRadius: "12px",
  border: "1px solid hsl(var(--border))",
  background: "hsl(var(--card))",
  fontSize: "12px",
};

export function AppointmentTrendChart({ data }: { data: TrendPoint[] }) {
  const formatted = data.map((d) => ({
    ...d,
    label: new Date(d.date).toLocaleDateString("en-IN", { weekday: "short" }),
  }));

  return (
    <div>
      <ResponsiveContainer width="100%" height={280}>
        <AreaChart data={formatted} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
          <defs>
            <linearGradient id="scheduledGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.25} />
              <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="completedGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#10b981" stopOpacity={0.2} />
              <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
          <XAxis
            dataKey="label"
            tick={{ fontSize: 11, fill: "hsl(var(--muted-foreground))" }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            tick={{ fontSize: 11, fill: "hsl(var(--muted-foreground))" }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip contentStyle={tooltipStyle} />
          <Area
            type="monotone"
            dataKey="scheduled"
            stroke="hsl(var(--primary))"
            strokeWidth={2}
            fill="url(#scheduledGrad)"
            name="Scheduled"
          />
          <Area
            type="monotone"
            dataKey="completed"
            stroke="#10b981"
            strokeWidth={2}
            fill="url(#completedGrad)"
            name="Completed"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
