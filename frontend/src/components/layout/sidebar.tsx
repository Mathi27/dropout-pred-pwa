import { ChevronLeft, ChevronRight, Sparkles } from "lucide-react";
import { NavLink } from "react-router-dom";

import { Button } from "@/components/ui/button";
import { getNavForRole } from "@/config/navigation";
import type { UserRole } from "@/lib/constants";
import { cn } from "@/lib/utils";

interface SidebarProps {
  role?: UserRole;
  collapsed?: boolean;
  onNavigate?: () => void;
  onToggleCollapse?: () => void;
}

export function Sidebar({ role, collapsed = false, onNavigate, onToggleCollapse }: SidebarProps) {
  if (!role) return null;
  const items = getNavForRole(role);

  return (
    <div className="flex h-full flex-col">
      <div
        className={cn(
          "flex h-16 items-center border-b border-sidebar-border",
          collapsed ? "justify-center px-2" : "justify-between px-5",
        )}
      >
        <div className={cn("flex items-center gap-2.5", collapsed && "justify-center")}>
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-teal-600 text-primary-foreground shadow-sm">
            <Sparkles className="h-4 w-4" />
          </div>
          {!collapsed && (
            <div className="overflow-hidden">
              <span className="block text-base font-bold tracking-tight text-primary">DentalAI</span>
              <span className="block text-[10px] font-medium uppercase tracking-widest text-muted-foreground">
                Care Platform
              </span>
            </div>
          )}
        </div>
        {onToggleCollapse && !collapsed && (
          <Button
            variant="ghost"
            size="icon"
            className="hidden h-8 w-8 shrink-0 lg:flex"
            onClick={onToggleCollapse}
            aria-label="Collapse sidebar"
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
        )}
      </div>

      <nav className="flex-1 space-y-1 p-3">
        {items.map((item) => (
          <NavLink
            key={item.href}
            to={item.href}
            onClick={onNavigate}
            title={collapsed ? item.title : undefined}
          >
            {({ isActive }) => (
              <span
                className={cn(
                  "flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-200",
                  collapsed && "justify-center px-2",
                  isActive
                    ? "nav-item-active"
                    : "text-muted-foreground hover:bg-sidebar-accent hover:text-foreground",
                )}
              >
                <item.icon
                  className={cn(
                    "h-[18px] w-[18px] shrink-0",
                    isActive ? "text-primary" : "text-muted-foreground",
                  )}
                />
                {!collapsed && <span className="truncate">{item.title}</span>}
              </span>
            )}
          </NavLink>
        ))}
      </nav>

      {onToggleCollapse && collapsed && (
        <div className="border-t border-sidebar-border p-3">
          <Button
            variant="ghost"
            size="icon"
            className="mx-auto h-8 w-8"
            onClick={onToggleCollapse}
            aria-label="Expand sidebar"
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      )}
    </div>
  );
}
