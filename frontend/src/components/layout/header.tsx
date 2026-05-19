import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { Bell, LogOut, Menu, Moon, Settings, Sun } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import { toast } from "sonner";

import { authApi } from "@/api/auth";
import { notificationsApi } from "@/api/notifications";
import { Sidebar } from "@/components/layout/sidebar";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { ROLE_LABELS } from "@/lib/constants";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/stores/auth-store";
import { useTheme } from "@/hooks/use-theme";

interface HeaderProps {
  sidebarCollapsed?: boolean;
}

export function Header({ sidebarCollapsed }: HeaderProps) {
  const navigate = useNavigate();
  const { user, refreshToken, logout } = useAuthStore();
  const { theme, setTheme } = useTheme();

  const initials =
    user?.full_name
      ?.split(" ")
      .map((n) => n[0])
      .join("")
      .slice(0, 2)
      .toUpperCase() || "DA";

  const { data: unread } = useQuery({
    queryKey: ["notifications-unread"],
    queryFn: () => notificationsApi.unreadCount().then((r) => r.data),
    enabled: !!user,
  });

  const handleLogout = async () => {
    try {
      if (refreshToken) await authApi.logout(refreshToken);
    } catch {
      /* ignore */
    }
    logout();
    toast.success("Signed out successfully");
    navigate("/login");
  };

  const toggleTheme = () => {
    setTheme(theme === "dark" ? "light" : "dark");
  };

  return (
    <header
      className={cn(
        "sticky top-0 z-40 flex h-16 items-center gap-3 border-b border-border/50",
        "bg-card/70 px-4 backdrop-blur-xl supports-[backdrop-filter]:bg-card/50",
        "lg:px-6",
        sidebarCollapsed && "lg:pl-6",
      )}
    >
      <Sheet>
        <SheetTrigger asChild>
          <Button variant="ghost" size="icon" className="rounded-xl lg:hidden">
            <Menu className="h-5 w-5" />
            <span className="sr-only">Open menu</span>
          </Button>
        </SheetTrigger>
        <SheetContent side="left" className="w-72 border-r-0 bg-sidebar p-0">
          {user && <Sidebar role={user.role} onNavigate={() => {}} />}
        </SheetContent>
      </Sheet>

      <div className="flex flex-1 items-center gap-2 lg:hidden">
        <span className="text-lg font-bold tracking-tight text-primary">DentalAI</span>
      </div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="ml-auto flex items-center gap-1"
      >
        <Button variant="ghost" size="icon" asChild className="relative rounded-xl">
          <Link to="/notifications" aria-label="Notifications">
            <Bell className="h-[18px] w-[18px]" />
            {(unread?.count ?? 0) > 0 && (
              <span className="absolute right-1 top-1 flex h-4 min-w-4 items-center justify-center rounded-full bg-primary px-1 text-[10px] font-bold text-primary-foreground ring-2 ring-card">
                {unread!.count > 9 ? "9+" : unread!.count}
              </span>
            )}
          </Link>
        </Button>

        <Button
          variant="ghost"
          size="icon"
          onClick={toggleTheme}
          className="rounded-xl"
          aria-label="Toggle theme"
        >
          {theme === "dark" ? <Sun className="h-[18px] w-[18px]" /> : <Moon className="h-[18px] w-[18px]" />}
        </Button>

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="relative ml-1 h-10 gap-2 rounded-xl px-2">
              <Avatar className="h-8 w-8 ring-2 ring-primary/20">
                <AvatarFallback className="bg-primary/10 text-xs font-semibold text-primary">
                  {initials}
                </AvatarFallback>
              </Avatar>
              <span className="hidden max-w-[120px] truncate text-sm font-medium md:inline">
                {user?.first_name}
              </span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-60 rounded-xl">
            <DropdownMenuLabel>
              <div className="flex flex-col space-y-1">
                <p className="text-sm font-semibold">{user?.full_name}</p>
                <p className="text-xs text-muted-foreground">{user?.email}</p>
                {user && (
                  <p className="text-xs font-medium text-primary">{ROLE_LABELS[user.role]}</p>
                )}
              </div>
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={() => navigate("/settings")} className="rounded-lg">
              <Settings className="mr-2 h-4 w-4" />
              Settings
            </DropdownMenuItem>
            <DropdownMenuItem onClick={handleLogout} className="rounded-lg text-destructive focus:text-destructive">
              <LogOut className="mr-2 h-4 w-4" />
              Sign out
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </motion.div>
    </header>
  );
}
