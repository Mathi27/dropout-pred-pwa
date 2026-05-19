import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export function SegmentationChart({
  data,
}: {
  data: { category: string; low: number; medium: number; high: number }[];
}) {
  return (
    <ResponsiveContainer width="100%" height={260}>
      <BarChart data={data} margin={{ top: 8, right: 8, left: -12, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
        <XAxis dataKey="category" tick={{ fontSize: 11, fill: "hsl(var(--muted-foreground))" }} axisLine={false} tickLine={false} />
        <YAxis tick={{ fontSize: 11, fill: "hsl(var(--muted-foreground))" }} axisLine={false} tickLine={false} />
        <Tooltip
          contentStyle={{
            borderRadius: "12px",
            border: "1px solid hsl(var(--border))",
            background: "hsl(var(--card))",
            fontSize: "12px",
          }}
        />
        <Bar dataKey="low" stackId="risk" fill="hsl(var(--risk-low))" />
        <Bar dataKey="medium" stackId="risk" fill="hsl(var(--risk-medium))" />
        <Bar dataKey="high" stackId="risk" fill="hsl(var(--risk-high))" />
      </BarChart>
    </ResponsiveContainer>
  );
}
