import { motion } from "framer-motion";

import type { ShapExplanation } from "@/types/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

function formatFeature(name: string) {
  return name.replace(/_/g, " ");
}

export function ShapExplanationCard({ explanation }: { explanation?: ShapExplanation }) {
  if (!explanation) {
    return (
      <Card className="glass-card border-0 shadow-card">
        <CardHeader>
          <CardTitle>Key risk drivers</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">Run a prediction to see model explanations.</p>
        </CardContent>
      </Card>
    );
  }

  const maxImpact = Math.max(...explanation.top_features.map((f) => f.impact), 1);

  return (
    <Card className="glass-card border-0 shadow-card">
      <CardHeader>
        <CardTitle>Key risk drivers</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {explanation.top_features.map((feature, i) => {
          const isPositive = feature.value >= 0;
          const barClass = isPositive
            ? "from-rose-500/80 to-amber-400/80"
            : "from-emerald-500/80 to-teal-400/80";
          const pillClass = isPositive
            ? "bg-rose-500/15 text-rose-600 dark:text-rose-300"
            : "bg-emerald-500/15 text-emerald-700 dark:text-emerald-300";
          const label = isPositive ? "Risk up" : "Risk down";
          return (
            <motion.div
              key={feature.feature}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              className="space-y-2"
            >
              <div className="flex items-center justify-between text-sm">
                <span className="font-medium">{formatFeature(feature.feature)}</span>
                <span className={`rounded-full px-2 py-0.5 text-[11px] font-semibold ${pillClass}`}>
                  {label}
                </span>
              </div>
              <div className="h-2 overflow-hidden rounded-full bg-muted">
                <div
                  className={`h-full rounded-full bg-gradient-to-r ${barClass}`}
                  style={{ width: `${(feature.impact / maxImpact) * 100}%` }}
                />
              </div>
              <div className="flex items-center justify-between text-xs text-muted-foreground">
                <span>{feature.value > 0 ? "+" : ""}{feature.value.toFixed(2)}</span>
                <span>Impact {feature.impact.toFixed(2)}</span>
              </div>
            </motion.div>
          );
        })}
      </CardContent>
    </Card>
  );
}
