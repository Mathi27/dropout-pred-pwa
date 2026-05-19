import { motion } from "framer-motion";

import type { AIPrediction } from "@/types/api";
import { RiskBadge } from "@/components/shared/risk-badge";

export function PredictionHistoryTimeline({ predictions }: { predictions: AIPrediction[] }) {
  if (!predictions.length) {
    return <p className="text-sm text-muted-foreground">No prediction history yet.</p>;
  }

  return (
    <div className="relative space-y-4 pl-5">
      <div className="absolute left-2 top-2 h-full w-px bg-border/60" />
      {predictions.map((p, i) => {
        const score = p.risk_score ?? Math.round(p.probability * 100);
        return (
          <motion.div
            key={p.id}
            initial={{ opacity: 0, x: -8 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.03 }}
            className="relative flex items-start gap-4"
          >
            <span className="mt-1 h-3 w-3 rounded-full bg-primary/60" />
            <div className="flex flex-1 flex-col gap-2 rounded-xl border border-border/50 bg-card/80 p-3">
              <div className="flex items-center justify-between gap-4">
                <div>
                  <p className="text-sm font-medium">
                    {new Date(p.created_at).toLocaleString("en-IN", {
                      dateStyle: "medium",
                      timeStyle: "short",
                    })}
                  </p>
                  <p className="text-xs text-muted-foreground">Model run</p>
                </div>
                <RiskBadge level={p.risk_level} score={score} />
              </div>
              <p className="text-xs text-muted-foreground">Confidence {Math.round(p.probability * 100)}%</p>
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}
