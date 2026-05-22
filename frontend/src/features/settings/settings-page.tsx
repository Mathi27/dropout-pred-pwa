import { motion } from "framer-motion";

import { PageHeader } from "@/components/shared/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { ROLE_LABELS } from "@/lib/constants";
import { useAuthStore } from "@/stores/auth-store";
import { useTheme } from "@/hooks/use-theme";

export function SettingsPage() {
  const user = useAuthStore((s) => s.user);
  const { theme, setTheme } = useTheme();

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
      <PageHeader title="Settings" description="Profile and preferences" />

      <Card className="max-w-lg ">
        <CardHeader>
          <CardTitle>Profile</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label className="text-muted-foreground">Name</Label>
            <p className="font-medium">{user?.first_name} {user?.last_name}</p>
          </div>
          <div>
            <Label className="text-muted-foreground">Email</Label>
            <p className="font-medium">{user?.email}</p>
          </div>
          <div>
            <Label className="text-muted-foreground">Role</Label>
            <p className="font-medium">{user ? ROLE_LABELS[user.role] : "—"}</p>
          </div>
          <div>
            <Label className="text-muted-foreground">Theme</Label>
            <button
              type="button"
              onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
              className="mt-1 text-sm font-medium text-primary hover:underline"
            >
              {theme === "dark" ? "Switch to light" : "Switch to dark"}
            </button>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
