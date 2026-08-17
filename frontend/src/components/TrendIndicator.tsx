import { Icon, type IconName } from "./Icon";

type Trend = "improving" | "stable" | "declining" | "new";

interface TrendIndicatorProps {
  trend: Trend;
  showLabel?: boolean;
}

const CONFIG: Record<Trend, { icon: IconName; color: string; label: string }> = {
  improving: { icon: "trend-up", color: "var(--color-success)", label: "Melhorando" },
  stable: { icon: "trend-flat", color: "var(--color-text-secondary)", label: "Estável" },
  declining: { icon: "trend-down", color: "var(--color-danger)", label: "Piorando" },
  new: { icon: "sparkle", color: "var(--color-card-black)", label: "Novo" },
};

export function TrendIndicator({ trend, showLabel = false }: TrendIndicatorProps) {
  const cfg = CONFIG[trend] ?? CONFIG.stable;
  return (
    <span className="inline-flex items-center gap-1" style={{ color: cfg.color }}>
      <Icon name={cfg.icon} size={16} />
      {showLabel && <span className="text-sm font-medium">{cfg.label}</span>}
    </span>
  );
}
