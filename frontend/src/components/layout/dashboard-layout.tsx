import { Outlet } from "react-router-dom";
import { motion } from "framer-motion";

import { Header } from "@/components/layout/header";
import { Sidebar } from "@/components/layout/sidebar";
import { useAuthStore } from "@/stores/auth-store";

export function DashboardLayout() {
  const user = useAuthStore((s) => s.user);

  return (
    <div className="flex min-h-screen bg-background">
      <aside className="hidden w-64 shrink-0 border-r bg-card lg:block">
        <div className="flex h-14 items-center border-b px-6">
          <span className="text-lg font-semibold tracking-tight text-primary">DentalAI</span>
        </div>
        {user && <Sidebar role={user.role} />}
      </aside>

      <div className="flex flex-1 flex-col">
        <Header />
        <main className="flex-1 overflow-auto p-4 lg:p-6">
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.25 }}
          >
            <Outlet />
          </motion.div>
        </main>
      </div>
    </div>
  );
}
