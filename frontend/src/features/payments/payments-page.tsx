import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { toast } from "sonner";

import { paymentsApi, patientTreatmentsApi } from "@/api/resources";
import { PageHeader } from "@/components/shared/page-header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { patientsApi } from "@/api/patients";
import { format } from "date-fns";
import { Badge } from "@/components/ui/badge";

export function PaymentsPage() {
  const qc = useQueryClient();
  const [isFormOpen, setFormOpen] = useState(false);

  const { data: payments, isLoading: isLoadingPayments } = useQuery({
    queryKey: ["payments"],
    queryFn: () => paymentsApi.list().then((r) => r.data),
  });

  const addPayment = useMutation({
    mutationFn: (newPayment: any) => paymentsApi.create(newPayment),
    onSuccess: () => {
      toast.success("Payment added successfully");
      qc.invalidateQueries({ queryKey: ["payments"] });
      qc.invalidateQueries({ queryKey: ["admin-analytics"] });
      setFormOpen(false);
    },
    onError: () => {
      toast.error("Failed to add payment");
    },
  });

  return (
    <div className="space-y-6">
      <PageHeader title="Payments">
        <Button onClick={() => setFormOpen((prev) => !prev)}>
          {isFormOpen ? "Cancel" : "Add New Payment"}
        </Button>
      </PageHeader>

      {isFormOpen && <AddPaymentForm mutation={addPayment} />}

      <div className="rounded-xl border border-border/50 bg-card/20 p-4 md:p-6">
        <h2 className="text-lg font-semibold mb-4">Payment History</h2>
        {isLoadingPayments ? (
          <Skeleton className="h-48 w-full" />
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Patient</TableHead>
                <TableHead>Treatment</TableHead>
                <TableHead>Amount</TableHead>
                <TableHead>Date</TableHead>
                <TableHead>Method</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {payments?.results?.map((p: any) => (
                <TableRow key={p.id}>
                  <TableCell>{p.patient_name}</TableCell>
                  <TableCell>{p.treatment_name}</TableCell>
                  <TableCell>₹{p.amount}</TableCell>
                  <TableCell>{format(new Date(p.payment_date), "dd MMM yyyy")}</TableCell>
                  <TableCell>{p.payment_method}</TableCell>
                  <TableCell><Badge variant={p.status === 'COMPLETED' ? 'success' : 'secondary'}>{p.status}</Badge></TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </div>
    </div>
  );
}

function AddPaymentForm({ mutation }: { mutation: any }) {
  const [patientId, setPatientId] = useState("");
  const [treatmentId, setTreatmentId] = useState("");
  const [amount, setAmount] = useState("");
  const [paymentDate, setPaymentDate] = useState(new Date().toISOString().split("T")[0]);
  const [paymentMethod, setPaymentMethod] = useState("CARD");

  const { data: patients, isLoading: isLoadingPatients } = useQuery({
    queryKey: ["patients-list"],
    queryFn: () => patientsApi.list({ limit: 1000 }).then((r) => r.data),
  });

  const { data: treatments, isLoading: isLoadingTreatments } = useQuery({
    queryKey: ["patient-treatments", patientId],
    queryFn: () => patientTreatmentsApi.list({ patient: patientId, limit: 1000 }).then((r) => r.data),
    enabled: !!patientId,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    mutation.mutate({
      patient: patientId,
      patient_treatment: treatmentId,
      amount,
      payment_date: paymentDate,
      payment_method: paymentMethod,
      status: "COMPLETED",
    });
  };

  return (
    <div className="rounded-xl border border-border/50 bg-card/20 p-4 md:p-6">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div>
            <Label htmlFor="patient">Patient</Label>
            <Select onValueChange={setPatientId} value={patientId} required>
              <SelectTrigger>
                <SelectValue placeholder="Select a patient" />
              </SelectTrigger>
              <SelectContent>
                {isLoadingPatients ? <SelectItem value="loading" disabled>Loading...</SelectItem> :
                  patients?.results?.map((p: any) => <SelectItem key={p.id} value={p.id}>{p.full_name}</SelectItem>)
                }
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label htmlFor="treatment">Treatment</Label>
            <Select onValueChange={setTreatmentId} value={treatmentId} disabled={!patientId || isLoadingTreatments} required>
              <SelectTrigger>
                <SelectValue placeholder="Select a treatment" />
              </SelectTrigger>
              <SelectContent>
                {isLoadingTreatments ? <SelectItem value="loading" disabled>Loading...</SelectItem> :
                  treatments?.results?.map((t: any) => <SelectItem key={t.id} value={t.id}>{t.treatment_detail.name}</SelectItem>)
                }
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label htmlFor="amount">Amount</Label>
            <Input id="amount" type="number" value={amount} onChange={(e) => setAmount(e.target.value)} required />
          </div>
          <div>
            <Label htmlFor="paymentDate">Payment Date</Label>
            <Input id="paymentDate" type="date" value={paymentDate} onChange={(e) => setPaymentDate(e.target.value)} required />
          </div>
          <div>
            <Label htmlFor="paymentMethod">Payment Method</Label>
            <Select onValueChange={setPaymentMethod} value={paymentMethod} required>
              <SelectTrigger>
                <SelectValue placeholder="Select a method" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="CARD">Card</SelectItem>
                <SelectItem value="CASH">Cash</SelectItem>
                <SelectItem value="UPI">UPI</SelectItem>
                <SelectItem value="BANK_TRANSFER">Bank Transfer</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
        <div className="flex justify-end">
          <Button type="submit" disabled={mutation.isPending}>
            {mutation.isPending ? "Saving..." : "Save Payment"}
          </Button>
        </div>
      </form>
    </div>
  );
}
