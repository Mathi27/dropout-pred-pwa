import { Badge } from "@/components/ui/badge";

type StatusVariant = "default" | "success" | "warning" | "destructive" | "muted";

const STATUS_MAP: Record<string, StatusVariant> = {
  scheduled: "default",
  confirmed: "default",
  completed: "success",
  cancelled: "destructive",
  present: "success",
  absent: "destructive",
  pending: "warning",
  no_show: "warning",
  in_progress: "warning",
};

interface StatusBadgeProps {
  status: string;
  className?: string;
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const variant = STATUS_MAP[status.toLowerCase()] ?? "muted";
  const label = status.replace(/_/g, " ");

  return (
    <Badge variant={variant} className={className}>
      {label}
    </Badge>
  );
}
