import { isAxiosError } from "axios";
import { motion } from "framer-motion";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { toast } from "sonner";

import { authApi } from "@/api/auth";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { extractApiErrors } from "@/lib/api-errors";
import { ROLES } from "@/lib/constants";
import type { UserRole } from "@/lib/constants";
import type { RegisterPayload } from "@/types/auth";
import { useAuthStore } from "@/stores/auth-store";

const EMPTY_FIELD_ERRORS: Record<string, string> = {};

export function RegisterPage() {
  const navigate = useNavigate();
  const setAuth = useAuthStore((s) => s.setAuth);
  const [form, setForm] = useState({
    email: "",
    password: "",
    password_confirm: "",
    first_name: "",
    last_name: "",
    phone: "",
    role: ROLES.PATIENT as UserRole,
  });
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>(EMPTY_FIELD_ERRORS);
  const [loading, setLoading] = useState(false);

  const update = (field: string, value: string) => {
    setFieldErrors((prev) => {
      if (!prev[field]) return prev;
      const next = { ...prev };
      delete next[field];
      return next;
    });
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const fieldError = (name: string) => fieldErrors[name];

  const buildPayload = (): RegisterPayload => ({
    email: form.email.trim().toLowerCase(),
    password: form.password,
    password_confirm: form.password_confirm,
    first_name: form.first_name.trim(),
    last_name: form.last_name.trim(),
    phone: form.phone.trim(),
    role: form.role,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFieldErrors(EMPTY_FIELD_ERRORS);

    if (form.password !== form.password_confirm) {
      const message = "Passwords do not match.";
      setFieldErrors({ password_confirm: message });
      toast.error(message);
      return;
    }

    const payload = buildPayload();
    setLoading(true);

    if (import.meta.env.DEV) {
      console.debug("[register] payload keys:", Object.keys(payload));
    }

    try {
      const { data } = await authApi.register(payload);
      setAuth(data.user, data.tokens.access, data.tokens.refresh);
      toast.success("Account created successfully");
      navigate("/dashboard", { replace: true });
    } catch (error) {
      const { message, fieldErrors: apiFieldErrors } = extractApiErrors(error);
      setFieldErrors(apiFieldErrors);

      if (import.meta.env.DEV && isAxiosError(error)) {
        console.debug("[register] error response:", error.response?.status, error.response?.data);
      }

      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-full max-w-md"
    >
      <Card className="">
        <CardHeader className="space-y-1 text-center">
          <CardTitle className="text-2xl">Create account</CardTitle>
          <CardDescription>Join DentalAI for smarter dental care</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              className="grid grid-cols-2 gap-3"
            >
              <motion.div className="space-y-2">
                <Label htmlFor="first_name">First name</Label>
                <Input
                  id="first_name"
                  value={form.first_name}
                  onChange={(e) => update("first_name", e.target.value)}
                  aria-invalid={Boolean(fieldError("first_name"))}
                />
                {fieldError("first_name") && (
                  <p className="text-xs text-destructive">{fieldError("first_name")}</p>
                )}
              </motion.div>
              <motion.div className="space-y-2">
                <Label htmlFor="last_name">Last name</Label>
                <Input
                  id="last_name"
                  value={form.last_name}
                  onChange={(e) => update("last_name", e.target.value)}
                  aria-invalid={Boolean(fieldError("last_name"))}
                />
                {fieldError("last_name") && (
                  <p className="text-xs text-destructive">{fieldError("last_name")}</p>
                )}
              </motion.div>
            </motion.div>
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                value={form.email}
                onChange={(e) => update("email", e.target.value)}
                required
                aria-invalid={Boolean(fieldError("email"))}
              />
              {fieldError("email") && (
                <p className="text-xs text-destructive">{fieldError("email")}</p>
              )}
            </div>
            <motion.div className="space-y-2">
              <Label htmlFor="phone">Phone (optional)</Label>
              <Input
                id="phone"
                type="tel"
                value={form.phone}
                onChange={(e) => update("phone", e.target.value)}
                aria-invalid={Boolean(fieldError("phone"))}
              />
              {fieldError("phone") && (
                <p className="text-xs text-destructive">{fieldError("phone")}</p>
              )}
            </motion.div>
            <div className="space-y-2">
              <Label htmlFor="role">Role</Label>
              <select
                id="role"
                value={form.role}
                onChange={(e) => update("role", e.target.value)}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                aria-invalid={Boolean(fieldError("role"))}
              >
                <option value={ROLES.PATIENT}>Patient</option>
                <option value={ROLES.DOCTOR}>Doctor</option>
                <option value={ROLES.RECEPTIONIST}>Receptionist</option>
              </select>
              {fieldError("role") && (
                <p className="text-xs text-destructive">{fieldError("role")}</p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                value={form.password}
                onChange={(e) => update("password", e.target.value)}
                required
                minLength={8}
                aria-invalid={Boolean(fieldError("password"))}
              />
              {fieldError("password") ? (
                <p className="text-xs text-destructive">{fieldError("password")}</p>
              ) : (
                <p className="text-xs text-muted-foreground">
                  At least 8 characters; avoid common or entirely numeric passwords.
                </p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="password_confirm">Confirm password</Label>
              <Input
                id="password_confirm"
                type="password"
                value={form.password_confirm}
                onChange={(e) => update("password_confirm", e.target.value)}
                required
                aria-invalid={Boolean(fieldError("password_confirm"))}
              />
              {fieldError("password_confirm") && (
                <p className="text-xs text-destructive">{fieldError("password_confirm")}</p>
              )}
            </div>
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? "Creating…" : "Create account"}
            </Button>
          </form>
          <p className="mt-6 text-center text-sm text-muted-foreground">
            Already have an account?{" "}
            <Link to="/login" className="font-medium text-primary hover:underline">
              Sign in
            </Link>
          </p>
        </CardContent>
      </Card>
    </motion.div>
  );
}
