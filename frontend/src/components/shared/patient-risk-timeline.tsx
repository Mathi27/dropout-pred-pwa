import { motion } from "framer-motion";

import { RiskBadge } from "@/components/shared/risk-badge";

const ICONS: Record<string, string> = {
  prediction: "AI",
  appointment: "AP",
  payment: "PM",
  intervention: "NT",
};

export function PatientRiskTimeline({
  events,
}: {
  events: {
    type: string;
    timestamp: string;
    status?: string;
    attendance?: string;
    risk_level?: string;
    probability?: number;
    amount?: number;
    notification_type?: string;
  }[];
}) {
  if (!events.length) {
    return <p className="text-sm text-muted-foreground">No timeline activity yet.</p>;
  }

  return (
    <div className="relative space-y-4 pl-5">
      <div className="absolute left-2 top-2 h-full w-px bg-border/60" />
      {events.map((event, index) => {
        const score = event.probability !== undefined ? Math.round(event.probability * 100) : undefined;
        return (
          <motion.div
            key={`${event.type}-${event.timestamp}-${index}`}
            initial={{ opacity: 0, x: -8 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.02 }}
            className="relative flex items-start gap-4"
          >
            <div className="mt-1 flex h-7 w-7 items-center justify-center rounded-full border border-border/60 bg-card text-[10px] font-semibold">
              {ICONS[event.type] ?? "EV"}
            </div>
            <div className="flex-1 rounded-xl border border-border/50 bg-card/80 p-3">
              <div className="flex items-center justify-between gap-4">
                <div>
                  <p className="text-sm font-medium capitalize">{event.type.replace(/_/g, " ")}</p>
                  <p className="text-xs text-muted-foreground">
                    {new Date(event.timestamp).toLocaleString("en-IN", {
                      dateStyle: "medium",
                      timeStyle: "short",
                    })}
                  </p>
                </div>
                {event.risk_level && score !== undefined ? (
                  <RiskBadge level={event.risk_level} score={score} />
                ) : null}
              </div>
              <div className="mt-2 flex flex-wrap gap-2 text-xs text-muted-foreground">
                {event.status ? <span>Status: {event.status}</span> : null}
                {event.attendance ? <span>Attendance: {event.attendance}</span> : null}
                {event.amount ? <span>Amount: {event.amount.toFixed(2)}</span> : null}
                {event.notification_type ? <span>Notification: {event.notification_type}</span> : null}
              </div>
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}
