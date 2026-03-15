import { LucideIcon } from "lucide-react";

interface StatsCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  variant?: "default" | "success" | "danger" | "primary";
  subtitle?: string;
}

export function StatsCard({ title, value, icon: Icon, variant = "default", subtitle }: StatsCardProps) {
  const variantStyles = {
    default: {
      container: "bg-card",
      icon: "bg-secondary text-foreground",
      value: "text-foreground",
    },
    success: {
      container: "bg-card",
      icon: "bg-success-soft text-success-soft-foreground",
      value: "text-success",
    },
    danger: {
      container: "bg-card",
      icon: "bg-fraud-soft text-fraud-soft-foreground",
      value: "text-fraud",
    },
    primary: {
      container: "bg-card",
      icon: "bg-primary/10 text-primary",
      value: "text-primary",
    },
  };

  const styles = variantStyles[variant];

  return (
    <div className={`${styles.container} rounded-xl border border-border p-6 shadow-card transition-all hover:shadow-soft`}>
      <div className="flex items-start justify-between">
        <div className="space-y-3">
          <p className="text-sm font-medium text-muted-foreground">{title}</p>
          <p className={`text-2xl font-semibold ${styles.value}`}>{value}</p>
          {subtitle && <p className="text-xs text-muted-foreground">{subtitle}</p>}
        </div>
        <div className={`w-12 h-12 rounded-lg ${styles.icon} flex items-center justify-center`}>
          <Icon className="w-6 h-6" />
        </div>
      </div>
    </div>
  );
}
