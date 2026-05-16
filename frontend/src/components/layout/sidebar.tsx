import { NavLink } from "react-router-dom";

import { cn } from "@/lib/utils";
import { getNavForRole } from "@/config/navigation";
import type { UserRole } from "@/lib/constants";

interface SidebarProps {
  role: UserRole;
  onNavigate?: () => void;
}

export function Sidebar({ role, onNavigate }: SidebarProps) {
  const items = getNavForRole(role);

  return (
    <nav className="flex flex-col gap-1 p-4">
      {items.map((item) => (
        <NavLink
          key={item.href}
          to={item.href}
          onClick={onNavigate}
          className={({ isActive }) =>
            cn(
              "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
              isActive
                ? "bg-primary/10 text-primary"
                : "text-muted-foreground hover:bg-accent hover:text-foreground",
            )
          }
        >
          <item.icon className="h-4 w-4 shrink-0" />
          {item.title}
        </NavLink>
      ))}
    </nav>
  );
}
