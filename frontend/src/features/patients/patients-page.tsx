import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { Users } from "lucide-react";
import { Link } from "react-router-dom";

import { patientsApi } from "@/api/patients";
import {
  DataTable,
  DataTableBody,
  DataTableCell,
  DataTableHead,
  DataTableHeader,
  DataTableRow,
} from "@/components/shared/data-table";
import { EmptyState } from "@/components/shared/empty-state";
import { PageHeader } from "@/components/shared/page-header";
import { PageSkeleton } from "@/components/shared/page-skeleton";
import { RiskBadge } from "@/components/shared/risk-badge";
import { Button } from "@/components/ui/button";

export function PatientsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["patients-risk"],
    queryFn: () => patientsApi.riskSorted().then((r) => r.data),
  });

  const patients = data?.results ?? [];

  if (isLoading) {
    return <PageSkeleton cards={0} rows={6} />;
  }

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-8">
      <PageHeader title="Patients" description="Sorted by dropout risk score" />

      {patients.length === 0 ? (
        <EmptyState icon={Users} title="No patients" description="Assigned patients will appear here." />
      ) : (
        <DataTable>
          <table className="w-full min-w-[640px]">
            <DataTableHeader>
              <DataTableHead>Patient</DataTableHead>
              <DataTableHead>Email</DataTableHead>
              <DataTableHead>Risk score</DataTableHead>
              <DataTableHead className="text-right">Action</DataTableHead>
            </DataTableHeader>
            <DataTableBody>
              {patients.map((p) => (
                <DataTableRow key={p.id}>
                  <DataTableCell>
                    <Link to={`/patients/${p.id}`} className="font-medium hover:text-primary">
                      {p.full_name}
                    </Link>
                  </DataTableCell>
                  <DataTableCell className="text-muted-foreground">{p.email}</DataTableCell>
                  <DataTableCell>
                    <RiskBadge score={p.risk_score} level={p.risk_level} />
                  </DataTableCell>
                  <DataTableCell className="text-right">
                    <Button variant="ghost" size="sm" asChild className="rounded-lg">
                      <Link to={`/patients/${p.id}`}>View</Link>
                    </Button>
                  </DataTableCell>
                </DataTableRow>
              ))}
            </DataTableBody>
          </table>
        </DataTable>
      )}
    </motion.div>
  );
}
