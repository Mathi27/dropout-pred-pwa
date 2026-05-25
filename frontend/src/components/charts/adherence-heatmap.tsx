const WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

export function AdherenceHeatmap({
  data,
}: {
  data: { weekday: number; present: number; absent: number; pending: number }[];
}) {
  return (
    <div className="grid grid-cols-7 gap-3">
      {data.map((cell) => {
        const total = cell.present + cell.absent + cell.pending;
        const missRate = total ? cell.absent / total : 0;
        return (
          <div key={cell.weekday} className="text-center">
            <div
              className="mx-auto flex h-12 w-12 items-center justify-center rounded-lg text-sm font-semibold"
              style={{
                background: `rgba(239, 68, 68, ${0.15 + missRate * 0.65})`,
              }}
            >
              {Math.round(missRate * 100)}
            </div>
            <span className="mt-2 block text-[11px] font-medium text-muted-foreground">
              {WEEKDAYS[cell.weekday]}
            </span>
          </div>
        );
      })}
    </div>
  );
}
