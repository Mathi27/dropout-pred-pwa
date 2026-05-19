import { motion } from "framer-motion";

import type { AIGeneratedMessage } from "@/types/api";
import { DeliveryStatusBadge } from "@/components/shared/delivery-status-badge";

export function CommunicationTimeline({ messages }: { messages: AIGeneratedMessage[] }) {
  if (!messages.length) {
    return <p className="text-sm text-muted-foreground">No communication history yet.</p>;
  }

  return (
    <div className="relative space-y-4 pl-5">
      <div className="absolute left-2 top-2 h-full w-px bg-border/60" />
      {messages.map((message, i) => (
        <motion.div
          key={message.id}
          initial={{ opacity: 0, x: -6 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: i * 0.04 }}
          className="relative flex items-start gap-4"
        >
          <span className="mt-2 h-3 w-3 rounded-full bg-primary/70" />
          <div className="flex-1 rounded-2xl border border-border/50 bg-card/80 p-4">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-sm font-semibold">
                  {message.message_type.replace(/_/g, " ")}
                </p>
                <p className="text-xs text-muted-foreground">
                  {new Date(message.created_at).toLocaleString("en-IN", {
                    dateStyle: "medium",
                    timeStyle: "short",
                  })}
                </p>
              </div>
              <DeliveryStatusBadge status={message.delivery_status} />
            </div>
            <p className="mt-3 text-sm text-foreground/90">{message.content}</p>
            <div className="mt-3 flex flex-wrap gap-2 text-xs text-muted-foreground">
              <span className="rounded-full border border-border/60 px-2 py-0.5">{message.language.toUpperCase()}</span>
              <span className="rounded-full border border-border/60 px-2 py-0.5">
                Confidence {(message.confidence_score * 100).toFixed(0)}%
              </span>
            </div>
          </div>
        </motion.div>
      ))}
    </div>
  );
}
