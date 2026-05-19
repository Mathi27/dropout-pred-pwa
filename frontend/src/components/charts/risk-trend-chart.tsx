import { motion } from "framer-motion";
import {
  Area,
  AreaChart,
  CartesianGrid,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { RiskTrendPoint } from "@/types/api";

const COLORS = {
  low: "hsl(var(--risk-low))",
  medium: "hsl(var(--risk-medium))",
  high: "hsl(var(--risk-high))",
};

export function RiskTrendChart({ data }: { data: RiskTrendPoint[] }) {
  const formatted = data.map((d) => ({
    ...d,
    label: new Date(d.date).toLocaleDateString("en-IN", { month: "short", day: "numeric" }),
  }));

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.15 }}>
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={formatted} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
          <defs>
            <linearGradient id="riskLow" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={COLORS.low} stopOpacity={0.35} />
              <stop offset="95%" stopColor={COLORS.low} stopOpacity={0} />
            </linearGradient>
            <linearGradient id="riskMedium" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={COLORS.medium} stopOpacity={0.35} />
              <stop offset="95%" stopColor={COLORS.medium} stopOpacity={0} />
            </linearGradient>
            <linearGradient id="riskHigh" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={COLORS.high} stopOpacity={0.35} />
              <stop offset="95%" stopColor={COLORS.high} stopOpacity={0} />
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
          <Tooltip
            content={({ active, payload, label }) => {
              if (!active || !payload?.length) return null;
              return (
                <div className="rounded-xl border border-border/60 bg-card/95 p-3 text-xs shadow-card">
                  <p className="mb-2 font-medium text-foreground">{label}</p>
                  <div className="space-y-1">
                    {payload.map((entry) => (
                      <div key={entry.name} className="flex items-center justify-between gap-6">
                        <span className="flex items-center gap-2 text-muted-foreground">
                          <span
                            className="h-2 w-2 rounded-full"
                            style={{ background: entry.color ?? "hsl(var(--foreground))" }}
                          />
                          {entry.name}
                        </span>
                        <span className="font-semibold text-foreground">{entry.value}</span>
                      </div>
                    ))}
                  </div>
                </div>
              );
            }}
          />
          <Area
            type="monotone"
            dataKey="low"
            stackId="1"
            stroke={COLORS.low}
            strokeWidth={2}
            fill="url(#riskLow)"
            name="Low risk"
          />
          <Area
            type="monotone"
            dataKey="medium"
            stackId="1"
            stroke={COLORS.medium}
            strokeWidth={2}
            fill="url(#riskMedium)"
            name="Medium risk"
          />
          <Area
            type="monotone"
            dataKey="high"
            stackId="1"
            stroke={COLORS.high}
            strokeWidth={2}
            fill="url(#riskHigh)"
            name="High risk"
          />
          <Line
            type="monotone"
            dataKey="total"
            stroke="hsl(var(--foreground))"
            strokeWidth={1.5}
            strokeOpacity={0.4}
            dot={false}
            name="Total"
          />
        </AreaChart>
      </ResponsiveContainer>
    </motion.div>
  );
}
