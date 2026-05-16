import {
  Calendar,
  ClipboardList,
  LayoutDashboard,
  Settings,
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
    roles: ["patient", "receptionist", "admin"],
  },
  {
    title: "Patients",
    href: "/patients",
    icon: Users,
    roles: ["doctor", "admin"],
  },
  {
    title: "Schedule",
    href: "/schedule",
    icon: ClipboardList,
    roles: ["receptionist", "admin"],
  },
  {
    title: "Clinical",
    href: "/clinical",
    icon: Stethoscope,
    roles: ["doctor"],
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
