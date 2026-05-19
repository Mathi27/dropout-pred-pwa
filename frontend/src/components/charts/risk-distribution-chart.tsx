import { Pie, PieChart, ResponsiveContainer, Tooltip, Cell } from "recharts";

const COLORS = {
  low: "hsl(var(--risk-low))",
  medium: "hsl(var(--risk-medium))",
  high: "hsl(var(--risk-high))",
};

const tooltipStyle = {
  borderRadius: "12px",
  border: "1px solid hsl(var(--border))",
  background: "hsl(var(--card))",
  boxShadow: "0 4px 16px -4px rgb(0 0 0 / 0.1)",
  fontSize: "12px",
};

export function RiskDistributionChart({
  data,
}: {
  data: { low: number; medium: number; high: number };
}) {
  const chartData = [
    { name: "Low", value: data.low, key: "low" },
    { name: "Medium", value: data.medium, key: "medium" },
    { name: "High", value: data.high, key: "high" },
  ];
  const total = chartData.reduce((sum, item) => sum + item.value, 0);

  if (!total) {
    return (
      <div className="flex h-[240px] items-center justify-center rounded-2xl border border-dashed border-border/60">
        <p className="text-sm text-muted-foreground">No distribution data yet.</p>
      </div>
    );
  }

  return (
    <div className="relative h-[240px]">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={chartData}
            dataKey="value"
            nameKey="name"
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={95}
            paddingAngle={3}
          >
            {chartData.map((entry) => (
              <Cell key={entry.name} fill={COLORS[entry.key as keyof typeof COLORS]} />
            ))}
          </Pie>
          <Tooltip contentStyle={tooltipStyle} />
        </PieChart>
      </ResponsiveContainer>
      <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
        <div className="text-center">
          <p className="text-xs uppercase tracking-wider text-muted-foreground">Total</p>
          <p className="text-2xl font-semibold">{total}</p>
        </div>
      </div>
    </div>
  );
}
