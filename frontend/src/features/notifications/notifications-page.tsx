import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { Bell } from "lucide-react";

import { notificationsApi } from "@/api/notifications";
import { EmptyState } from "@/components/shared/empty-state";
import { PageHeader } from "@/components/shared/page-header";
import { PageSkeleton } from "@/components/shared/page-skeleton";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";

export function NotificationsPage() {
  const qc = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ["notifications"],
    queryFn: () => notificationsApi.list().then((r) => r.data),
  });

  const markRead = useMutation({
    mutationFn: (id: string) => notificationsApi.markRead(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["notifications"] }),
  });

  const markAll = useMutation({
    mutationFn: () => notificationsApi.markAllRead(),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["notifications"] }),
  });

  if (isLoading) {
    return <PageSkeleton cards={0} rows={5} />;
  }

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-8">
      <PageHeader title="Notifications" description="Alerts and reminders">
        <Button
          variant="outline"
          size="sm"
          className="rounded-xl"
          onClick={() => markAll.mutate()}
          disabled={markAll.isPending}
        >
          Mark all read
        </Button>
      </PageHeader>

      {data?.results?.length ? (
        <div className="space-y-2">
          {data.results.map((n, i) => (
            <motion.div
              key={n.id}
              layout
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.03 }}
            >
              <Card
                className={cn(
                  "glass-card cursor-pointer border-0 transition-all hover:shadow-elevated",
                  !n.is_read && "ring-1 ring-primary/30",
                )}
                onClick={() => !n.is_read && markRead.mutate(n.id)}
              >
                <CardContent className="flex gap-4 p-5">
                  <div
                    className={cn(
                      "flex h-10 w-10 shrink-0 items-center justify-center rounded-xl",
                      n.is_read ? "bg-muted" : "bg-primary/10",
                    )}
                  >
                    <Bell className={cn("h-5 w-5", !n.is_read && "text-primary")} />
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-start justify-between gap-2">
                      <p className={cn("font-medium", !n.is_read && "text-foreground")}>{n.title}</p>
                      {!n.is_read && (
                        <span className="h-2 w-2 shrink-0 rounded-full bg-primary ring-4 ring-primary/20" />
                      )}
                    </div>
                    <p className="mt-1 text-sm leading-relaxed text-muted-foreground">{n.body}</p>
                    <p className="mt-2 text-xs text-muted-foreground">
                      {new Date(n.created_at).toLocaleString("en-IN")} · {n.notification_type}
                    </p>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      ) : (
        <EmptyState icon={Bell} title="All caught up" description="No notifications yet." />
      )}
    </motion.div>
  );
}
