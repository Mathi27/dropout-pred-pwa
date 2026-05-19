import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

const COLORS = {
  delivered: "hsl(var(--risk-low))",
  failed: "hsl(var(--risk-high))",
  queued: "hsl(var(--risk-medium))",
  sent: "hsl(var(--primary))",
};

const tooltipStyle = {
  borderRadius: "12px",
  border: "1px solid hsl(var(--border))",
  background: "hsl(var(--card))",
  boxShadow: "0 4px 16px -4px rgb(0 0 0 / 0.1)",
  fontSize: "12px",
};

export function DeliveryStatusChart({
  data,
}: {
  data: { status: string; count: number }[];
}) {
  if (!data.length) {
    return (
      <div className="flex h-[220px] items-center justify-center rounded-2xl border border-dashed border-border/60">
        <p className="text-sm text-muted-foreground">No delivery data yet.</p>
      </div>
    );
  }

  return (
    <div className="h-[220px]">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            dataKey="count"
            nameKey="status"
            cx="50%"
            cy="50%"
            innerRadius={55}
            outerRadius={90}
            paddingAngle={3}
          >
            {data.map((entry) => (
              <Cell key={entry.status} fill={COLORS[entry.status] ?? "hsl(var(--muted-foreground))"} />
            ))}
          </Pie>
          <Tooltip contentStyle={tooltipStyle} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
