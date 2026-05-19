import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

const LEVELS = {
  low: { label: "Low", variant: "success" as const },
  medium: { label: "Medium", variant: "warning" as const },
  high: { label: "High", variant: "destructive" as const },
};

function levelFromScore(score?: number) {
  if (score === undefined || Number.isNaN(score)) return undefined;
  if (score > 70) return "high";
  if (score > 40) return "medium";
  return "low";
}

export function RiskBadge({
  score,
  level,
  showScore = true,
  className,
}: {
  score?: number;
  level?: string | null;
  showScore?: boolean;
  className?: string;
}) {
  const normalized = (level ?? levelFromScore(score)) as keyof typeof LEVELS | undefined;
  if (!normalized || !(normalized in LEVELS)) {
    return (
      <Badge variant="muted" className={className}>
        Unknown
      </Badge>
    );
  }
  const config = LEVELS[normalized];
  return (
    <Badge variant={config.variant} className={cn("gap-1", className)}>
      {config.label}
      {showScore && score !== undefined ? <span>{score}%</span> : null}
    </Badge>
  );
}
