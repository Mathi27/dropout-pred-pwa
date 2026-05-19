import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { Shield } from "lucide-react";

import { auditLogsApi } from "@/api/resources";
import { EmptyState } from "@/components/shared/empty-state";
import { PageHeader } from "@/components/shared/page-header";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

export function AuditLogsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["audit-logs"],
    queryFn: () => auditLogsApi.list().then((r) => r.data),
  });

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
      <PageHeader title="Audit logs" description="System activity trail (admin only)" />

      {isLoading ? (
        <Skeleton className="h-64 w-full" />
      ) : data?.results?.length ? (
        <div className="space-y-2">
          {data.results.map((log) => (
            <Card key={log.id} className="glass-card border-0 shadow-card">
              <CardContent className="flex flex-wrap items-center justify-between gap-2 p-4 text-sm">
                <div>
                  <p className="font-medium">{log.action}</p>
                  <p className="text-muted-foreground">
                    {log.resource_type} · {log.resource_id}
                  </p>
                </div>
                <motion.div className="text-right text-muted-foreground">
                  <p>{log.actor_detail?.full_name ?? "System"}</p>
                  <p className="text-xs">{new Date(log.created_at).toLocaleString("en-IN")}</p>
                </motion.div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <EmptyState icon={Shield} title="No audit entries" description="Actions will be logged here." />
      )}
    </motion.div>
  );
}
