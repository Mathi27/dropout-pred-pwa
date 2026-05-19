import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

interface CompletionPoint {
  week: string;
  avg_progress: number;
}

export function CompletionTrendChart({ data }: { data: CompletionPoint[] }) {
  const formatted = data.map((d) => ({
    ...d,
    label: new Date(d.week).toLocaleDateString("en-IN", { month: "short", day: "numeric" }),
  }));

  return (
    <ResponsiveContainer width="100%" height={240}>
      <AreaChart data={formatted} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
        <defs>
          <linearGradient id="completionGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.35} />
            <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
        <XAxis dataKey="label" tick={{ fontSize: 11, fill: "hsl(var(--muted-foreground))" }} axisLine={false} tickLine={false} />
        <YAxis tick={{ fontSize: 11, fill: "hsl(var(--muted-foreground))" }} axisLine={false} tickLine={false} />
        <Tooltip
          contentStyle={{
            borderRadius: "12px",
            border: "1px solid hsl(var(--border))",
            background: "hsl(var(--card))",
            fontSize: "12px",
          }}
        />
        <Area
          type="monotone"
          dataKey="avg_progress"
          stroke="hsl(var(--primary))"
          strokeWidth={2}
          fill="url(#completionGrad)"
          name="Completion"
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
