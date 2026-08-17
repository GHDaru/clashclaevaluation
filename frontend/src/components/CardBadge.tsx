import { Icon } from "./Icon";
import type { IconName } from "./Icon";

interface CardBadgeProps {
  type: "yellow" | "red" | "black";
  count: number;
}

const CONFIG: Record<
  CardBadgeProps["type"],
  { icon: IconName; color: string; bg: string; glow: string }
> = {
  yellow: {
    icon: "card-yellow",
    color: "var(--color-card-yellow)",
    bg: "var(--color-card-yellow-bg)",
    glow: "rgba(250, 204, 21, 0.2)",
  },
  red: {
    icon: "card-red",
    color: "var(--color-card-red)",
    bg: "var(--color-card-red-bg)",
    glow: "rgba(239, 68, 68, 0.2)",
  },
  black: {
    icon: "card-black",
    color: "var(--color-card-black)",
    bg: "var(--color-card-black-bg)",
    glow: "rgba(99, 102, 241, 0.2)",
  },
};

export function CardBadge({ type, count }: CardBadgeProps) {
  if (count === 0) return null;
  const cfg = CONFIG[type];
  return (
    <div
      className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-[var(--radius-sm)] animate-scale-in"
      style={{
        backgroundColor: cfg.bg,
        color: cfg.color,
        boxShadow: `0 0 12px ${cfg.glow}`,
      }}
    >
      <Icon name={cfg.icon} size={14} />
      <span className="tabular-nums text-sm font-bold">{count}</span>
    </div>
  );
}
