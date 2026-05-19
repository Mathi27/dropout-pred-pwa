import { motion } from "framer-motion";

import type { AIPrediction } from "@/types/api";
import { RiskBadge } from "@/components/shared/risk-badge";

export function RiskActivityTimeline({ predictions }: { predictions: AIPrediction[] }) {
  if (!predictions.length) {
    return <p className="text-sm text-muted-foreground">No recent high-risk alerts.</p>;
  }

  return (
    <div className="relative space-y-4 pl-5">
      <div className="absolute left-2 top-2 h-full w-px bg-border/60" />
      {predictions.map((prediction, i) => {
        const score = prediction.risk_score ?? Math.round(prediction.probability * 100);
        return (
          <motion.div
            key={prediction.id}
            initial={{ opacity: 0, x: -8 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.04 }}
            className="relative flex items-start gap-4"
          >
            <span className="mt-1 h-3 w-3 rounded-full bg-destructive/80 shadow-sm" />
            <div className="flex-1 rounded-xl border border-border/50 bg-card/80 p-3">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-sm font-medium">
                    {prediction.patient_detail?.full_name ?? "Patient"}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {new Date(prediction.created_at).toLocaleString("en-IN", {
                      dateStyle: "medium",
                      timeStyle: "short",
                    })}
                  </p>
                </div>
                <RiskBadge level={prediction.risk_level} score={score} />
              </div>
              <p className="mt-2 text-xs text-muted-foreground">Latest high-risk signal</p>
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}
