import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

interface DataTableProps {
  children: ReactNode;
  className?: string;
}

export function DataTable({ children, className }: DataTableProps) {
  return (
    <div
      className={cn(
        "overflow-hidden rounded-2xl border border-border/50 bg-card shadow-card",
        className,
      )}
    >
      <div className="scrollbar-thin overflow-x-auto">{children}</div>
    </div>
  );
}

interface DataTableHeaderProps {
  children: ReactNode;
}

export function DataTableHeader({ children }: DataTableHeaderProps) {
  return (
    <thead className="sticky top-0 z-10 border-b bg-muted/50 backdrop-blur-sm">
      <tr>{children}</tr>
    </thead>
  );
}

interface DataTableHeadProps {
  children: ReactNode;
  className?: string;
}

export function DataTableHead({ children, className }: DataTableHeadProps) {
  return (
    <th
      className={cn(
        "px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted-foreground",
        className,
      )}
    >
      {children}
    </th>
  );
}

interface DataTableBodyProps {
  children: ReactNode;
}

export function DataTableBody({ children }: DataTableBodyProps) {
  return <tbody className="divide-y divide-border/50">{children}</tbody>;
}

interface DataTableRowProps {
  children: ReactNode;
  className?: string;
}

export function DataTableRow({ children, className }: DataTableRowProps) {
  return (
    <tr className={cn("transition-colors hover:bg-muted/30", className)}>{children}</tr>
  );
}

interface DataTableCellProps {
  children: ReactNode;
  className?: string;
}

export function DataTableCell({ children, className }: DataTableCellProps) {
  return <td className={cn("px-4 py-3 text-sm", className)}>{children}</td>;
}
