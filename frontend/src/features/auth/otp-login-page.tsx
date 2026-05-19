import { motion } from "framer-motion";
import { useState } from "react";
import { Link } from "react-router-dom";
import { toast } from "sonner";

import { apiClient } from "@/api/client";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export function OtpLoginPage() {
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [step, setStep] = useState<"request" | "verify">("request");
  const [loading, setLoading] = useState(false);

  const requestOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const { data } = await apiClient.post<{ debug_code?: string }>("/auth/otp/request/", {
        email,
        purpose: "login",
        debug: import.meta.env.DEV,
      });
      if (data.debug_code) toast.message(`Dev OTP: ${data.debug_code}`);
      setStep("verify");
      toast.success("OTP sent to your email");
    } catch {
      toast.error("Failed to send OTP");
    } finally {
      setLoading(false);
    }
  };

  const verifyOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await apiClient.post("/auth/otp/verify/", { email, code, purpose: "login" });
      toast.success("OTP verified — use password login for full session (stub)");
    } catch {
      toast.error("Invalid or expired OTP");
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="w-full max-w-md">
      <Card className="border-0 shadow-card">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl">Sign in with OTP</CardTitle>
          <CardDescription>Passwordless login (UI stub — wire to full flow in Phase 3)</CardDescription>
        </CardHeader>
        <CardContent>
          {step === "request" ? (
            <form onSubmit={requestOtp} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
              </div>
              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? "Sending…" : "Send OTP"}
              </Button>
            </form>
          ) : (
            <form onSubmit={verifyOtp} className="space-y-4">
              <motion.div initial={{ opacity: 0, x: 8 }} animate={{ opacity: 1, x: 0 }} className="space-y-2">
                <Label htmlFor="code">6-digit code</Label>
                <Input
                  id="code"
                  inputMode="numeric"
                  maxLength={6}
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                  required
                />
              </motion.div>
              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? "Verifying…" : "Verify OTP"}
              </Button>
              <Button type="button" variant="ghost" className="w-full" onClick={() => setStep("request")}>
                Resend code
              </Button>
            </form>
          )}
          <p className="mt-6 text-center text-sm">
            <Link to="/login" className="text-primary hover:underline">
              Use password instead
            </Link>
          </p>
        </CardContent>
      </Card>
    </motion.div>
  );
}
