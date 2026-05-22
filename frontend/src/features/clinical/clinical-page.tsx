import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { FileText } from "lucide-react";

import { clinicalNotesApi } from "@/api/resources";
import { EmptyState } from "@/components/shared/empty-state";
import { PageHeader } from "@/components/shared/page-header";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

export function ClinicalPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["clinical-notes"],
    queryFn: () => clinicalNotesApi.list().then((r) => r.data),
  });

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
      <PageHeader title="Clinical notes" description="Patient visit documentation" />

      {isLoading ? (
        <Skeleton className="h-48 w-full" />
      ) : data?.results?.length ? (
        <motion.div className="space-y-3">
          {data.results.map((n) => (
            <Card key={n.id} className="">
              <CardContent className="p-4">
                <p className="text-xs text-muted-foreground">{n.visit_date}</p>
                <p className="mt-2">{n.content}</p>
              </CardContent>
            </Card>
          ))}
        </motion.div>
      ) : (
        <EmptyState icon={FileText} title="No clinical notes" description="Create notes from a patient profile." />
      )}
    </motion.div>
  );
}
