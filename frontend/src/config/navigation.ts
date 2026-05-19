import {
  Bell,
  Brain,
  Calendar,
  ClipboardList,
  LayoutDashboard,
  MessagesSquare,
  Send,
  Settings,
  Shield,
  Stethoscope,
  Users,
  type LucideIcon,
} from "lucide-react";

import type { UserRole } from "@/lib/constants";

export interface NavItem {
  title: string;
  href: string;
  icon: LucideIcon;
  roles: UserRole[];
}

export const NAV_ITEMS: NavItem[] = [
  {
    title: "Dashboard",
    href: "/dashboard",
    icon: LayoutDashboard,
    roles: ["patient", "doctor", "receptionist", "admin"],
  },
  {
    title: "Appointments",
    href: "/appointments",
    icon: Calendar,
    roles: ["patient", "doctor", "receptionist", "admin"],
  },
  {
    title: "Notifications",
    href: "/notifications",
    icon: Bell,
    roles: ["patient", "doctor", "receptionist", "admin"],
  },
  {
    title: "Patients",
    href: "/patients",
    icon: Users,
    roles: ["doctor", "admin"],
  },
  {
    title: "AI Insights",
    href: "/ai-insights",
    icon: Brain,
    roles: ["doctor", "admin"],
  },
  {
    title: "Interventions",
    href: "/interventions",
    icon: MessagesSquare,
    roles: ["doctor", "admin"],
  },
  {
    title: "Clinical",
    href: "/clinical",
    icon: Stethoscope,
    roles: ["doctor"],
  },
  {
    title: "Schedule",
    href: "/schedule",
    icon: ClipboardList,
    roles: ["receptionist", "admin"],
  },
  {
    title: "Reminders",
    href: "/reminders",
    icon: Send,
    roles: ["receptionist"],
  },
  {
    title: "Users",
    href: "/admin/users",
    icon: Users,
    roles: ["admin"],
  },
  {
    title: "Audit logs",
    href: "/admin/audit",
    icon: Shield,
    roles: ["admin"],
  },
  {
    title: "Settings",
    href: "/settings",
    icon: Settings,
    roles: ["patient", "doctor", "receptionist", "admin"],
  },
];

export function getNavForRole(role: UserRole): NavItem[] {
  return NAV_ITEMS.filter((item) => item.roles.includes(role));
}
