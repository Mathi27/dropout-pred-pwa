import { useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { Send } from "lucide-react";
import { toast } from "sonner";

import { notificationsApi } from "@/api/notifications";
import { PageHeader } from "@/components/shared/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export function RemindersPage() {
  const qc = useQueryClient();
  const [userId, setUserId] = useState("");
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await notificationsApi.create({
        user: userId,
        title,
        body,
        notification_type: "reminder",
      });
      qc.invalidateQueries({ queryKey: ["notifications"], exact: false });
      qc.invalidateQueries({ queryKey: ["notifications-unread"] });
      toast.success("Reminder sent");
      setTitle("");
      setBody("");
    } catch {
      toast.error("Failed to send reminder");
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-8">
      <PageHeader title="Send reminder" description="Manual patient notification" />

      <Card className="max-w-lg ">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-primary/10">
              <Send className="h-4 w-4 text-primary" />
            </div>
            New reminder
          </CardTitle>
          <CardDescription>Send a custom notification to a patient</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label>User ID (UUID)</Label>
              <Input
                value={userId}
                onChange={(e) => setUserId(e.target.value)}
                required
                placeholder="Patient user UUID"
              />
            </div>
            <div className="space-y-2">
              <Label>Title</Label>
              <Input value={title} onChange={(e) => setTitle(e.target.value)} required />
            </div>
            <div className="space-y-2">
              <Label>Message</Label>
              <Input value={body} onChange={(e) => setBody(e.target.value)} required />
            </div>
            <Button type="submit" disabled={loading} className="w-full rounded-xl">
              {loading ? "Sending…" : "Send reminder"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </motion.div>
  );
}
