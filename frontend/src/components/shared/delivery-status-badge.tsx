import { Badge } from "@/components/ui/badge";

const STATUS_MAP: Record<string, { label: string; variant: "default" | "success" | "warning" | "destructive" | "muted" }> = {
  preview: { label: "Preview", variant: "muted" },
  queued: { label: "Queued", variant: "warning" },
  sent: { label: "Sent", variant: "default" },
  delivered: { label: "Delivered", variant: "success" },
  failed: { label: "Failed", variant: "destructive" },
};

export function DeliveryStatusBadge({ status }: { status?: string }) {
  if (!status) {
    return <Badge variant="muted">Unknown</Badge>;
  }
  const key = status.toLowerCase();
  const config = STATUS_MAP[key] ?? { label: status, variant: "muted" };
  return <Badge variant={config.variant}>{config.label}</Badge>;
}
