import { motion } from "framer-motion";

import { cn } from "@/lib/utils";

interface PageHeaderProps {
  title: string;
  description?: string;
  children?: React.ReactNode;
  className?: string;
  titleClassName?: string;
  descriptionClassName?: string;
  actionsClassName?: string;
}

export function PageHeader({
  title,
  description,
  children,
  className,
  titleClassName,
  descriptionClassName,
  actionsClassName,
}: PageHeaderProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={cn("flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between", className)}
    >
      <div className="space-y-1">
        <h1 className={cn("text-3xl font-bold tracking-tight text-balance", titleClassName)}>
          {title}
        </h1>
        {description && (
          <p className={cn("text-base text-muted-foreground", descriptionClassName)}>
            {description}
          </p>
        )}
      </div>
      {children && (
        <div className={cn("flex flex-wrap items-center gap-2", actionsClassName)}>
          {children}
        </div>
      )}
    </motion.div>
  );
}
