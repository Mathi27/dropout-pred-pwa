import { motion } from "framer-motion";

const WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

export function AdherenceHeatmap({
  data,
}: {
  data: { weekday: number; present: number; absent: number; pending: number }[];
}) {
  const totals = data.map((d) => d.present + d.absent + d.pending);
  const max = Math.max(...totals, 1);

  return (
    <div className="grid grid-cols-7 gap-3">
      {data.map((cell) => {
        const total = cell.present + cell.absent + cell.pending;
        const missRate = total ? cell.absent / total : 0;
        const intensity = total / max;
        return (
          <motion.div
            key={cell.weekday}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="text-center"
          >
            <div
              className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl text-sm font-semibold"
              style={{
                background: `rgba(239, 68, 68, ${0.15 + missRate * 0.65})`,
                boxShadow: intensity > 0.6 ? "0 6px 20px -10px rgba(239, 68, 68, 0.5)" : "none",
              }}
            >
              {Math.round(missRate * 100)}
            </div>
            <span className="mt-2 block text-[11px] font-medium text-muted-foreground">
              {WEEKDAYS[cell.weekday]}
            </span>
          </motion.div>
        );
      })}
    </div>
  );
}
