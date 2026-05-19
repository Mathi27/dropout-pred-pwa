import { motion } from "framer-motion";
import { Outlet } from "react-router-dom";
import { Sparkles } from "lucide-react";

export function AuthLayout() {
  return (
    <div className="relative flex min-h-screen flex-col items-center justify-center overflow-hidden p-4">
      <div className="pointer-events-none absolute inset-0 bg-gradient-to-br from-teal-50/80 via-white to-slate-100 dark:from-slate-950 dark:via-background dark:to-teal-950/30" />
      <div className="pointer-events-none absolute -left-32 -top-32 h-96 w-96 rounded-full bg-primary/10 blur-3xl" />
      <div className="pointer-events-none absolute -bottom-32 -right-32 h-96 w-96 rounded-full bg-teal-400/10 blur-3xl" />

      <motion.div
        initial={{ opacity: 0, y: -12 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative mb-8 flex items-center gap-3"
      >
        <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-br from-primary to-teal-600 text-primary-foreground shadow-elevated">
          <Sparkles className="h-5 w-5" />
        </div>
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-primary">DentalAI</h1>
          <p className="text-xs text-muted-foreground">Treatment adherence platform</p>
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="relative z-10 w-full max-w-md"
      >
        <Outlet />
      </motion.div>

      <p className="relative z-10 mt-10 text-center text-xs text-muted-foreground">
        DentalAI · INAHS 2026 Research · Treatment Adherence Platform
      </p>
    </div>
  );
}
