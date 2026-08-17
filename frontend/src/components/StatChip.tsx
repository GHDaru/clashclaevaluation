import type { ReactNode } from "react";
import { Icon, type IconName } from "./Icon";

interface StatChipProps {
  label: string;
  value: ReactNode;
  sublabel?: string;
  icon?: IconName;
  color?: "default" | "yellow" | "red" | "black" | "green" | "blue";
  size?: "sm" | "lg";
}

const COLORS: Record<string, string> = {
  default: "text-[var(--color-text-primary)]",
  yellow: "text-[var(--color-card-yellow)]",
  red: "text-[var(--color-card-red)]",
  black: "text-[var(--color-card-black)]",
  green: "text-[var(--color-success)]",
  blue: "text-[var(--color-info)]",
};

export function StatChip({ label, value, sublabel, icon, color = "default", size = "sm" }: StatChipProps) {
  return (
    <div className="flex flex-col items-center gap-1">
      <span className="text-[var(--color-text-tertiary)] text-xs font-medium uppercase tracking-wide">
        {label}
      </span>
      <div className={`flex items-center gap-1.5 tabular-nums font-bold ${COLORS[color]}`}>
        {icon && <Icon name={icon} size={size === "lg" ? 18 : 14} />}
        <span className={size === "lg" ? "text-2xl" : "text-lg"}>{value}</span>
      </div>
      {sublabel && (
        <span className="text-[var(--color-text-tertiary)] text-xs tabular-nums">
          {sublabel}
        </span>
      )}
    </div>
  );
}
