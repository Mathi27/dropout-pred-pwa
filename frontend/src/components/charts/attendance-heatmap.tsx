import { motion } from "framer-motion";

import { cn } from "@/lib/utils";

interface HeatmapCell {
  date: string;
  present: number;
  absent: number;
  pending: number;
}

export function AttendanceHeatmap({ data }: { data: HeatmapCell[] }) {
  const max = Math.max(...data.map((d) => d.present + d.absent + d.pending), 1);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="grid grid-cols-7 gap-3"
    >
      {data.map((cell, i) => {
        const total = cell.present + cell.absent + cell.pending;
        const intensity = total / max;
        return (
          <motion.div
            key={cell.date}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: i * 0.04 }}
            whileHover={{ scale: 1.06 }}
            className="text-center"
          >
            <div
              className={cn(
                "mx-auto flex h-12 w-12 items-center justify-center rounded-2xl text-sm font-semibold transition-shadow",
                intensity > 0.6
                  ? "bg-primary text-primary-foreground shadow-md"
                  : intensity > 0.3
                    ? "bg-primary/40 text-foreground"
                    : "bg-muted text-muted-foreground",
              )}
              title={`${cell.date}: ${cell.present} present, ${cell.absent} absent`}
            >
              {cell.present}
            </div>
            <span className="mt-2 block text-[11px] font-medium text-muted-foreground">
              {new Date(cell.date).toLocaleDateString("en-IN", { weekday: "short" })}
            </span>
          </motion.div>
        );
      })}
    </motion.div>
  );
}
