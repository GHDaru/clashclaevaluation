import { Icon, type IconName } from "./Icon";

type Status = "clean" | "warning" | "danger" | "critical";

interface StatusBadgeProps {
  status: Status;
}

const CONFIG: Record<Status, { label: string; icon: IconName; color: string; bg: string }> = {
  clean: {
    label: "Limpo",
    icon: "check",
    color: "var(--color-success)",
    bg: "var(--color-success-bg)",
  },
  warning: {
    label: "Alerta",
    icon: "alert",
    color: "var(--color-warning)",
    bg: "var(--color-warning-bg)",
  },
  danger: {
    label: "Perigo",
    icon: "fire",
    color: "var(--color-danger)",
    bg: "var(--color-danger-bg)",
  },
  critical: {
    label: "Crítico",
    icon: "fire",
    color: "#fca5a5",
    bg: "rgba(239, 68, 68, 0.2)",
  },
};

export function StatusBadge({ status }: StatusBadgeProps) {
  const cfg = CONFIG[status] ?? CONFIG.clean;
  return (
    <span
      className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-[var(--radius-pill)] text-xs font-semibold"
      style={{ backgroundColor: cfg.bg, color: cfg.color }}
    >
      <Icon name={cfg.icon} size={12} />
      {cfg.label}
    </span>
  );
}
