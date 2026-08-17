import type { PlayerStatusDTO } from "../types/domain";
import { Card } from "./Card";
import { StatusBadge } from "./StatusBadge";
import { CardBadge } from "./CardBadge";
import { TrendIndicator } from "./TrendIndicator";
import { StatChip } from "./StatChip";
import { Icon } from "./Icon";

interface PlayerCardProps {
  player: PlayerStatusDTO;
  onClick?: (tag: string) => void;
  index?: number;
}

const ROLE_LABELS: Record<string, string> = {
  leader: "Líder",
  coLeader: "Co-Líder",
  elder: "Veterano",
  member: "Membro",
};

const ROLE_COLORS: Record<string, string> = {
  leader: "var(--color-accent)",
  coLeader: "var(--color-accent-hover)",
  elder: "var(--color-info)",
  member: "var(--color-text-tertiary)",
};

export function PlayerCard({ player, onClick, index = 0 }: PlayerCardProps) {
  const tagForClick = (player.tag ?? "").replace("#", "");
  const hasCards = (player.yellow_cards ?? 0) > 0 || (player.red_cards ?? 0) > 0 || (player.black_cards ?? 0) > 0;
  const hasTrend = player.trend && player.trend !== "new";

  const handleClick = () => onClick?.(tagForClick);
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      handleClick();
    }
  };

  return (
    <Card
      interactive={!!onClick}
      onClick={onClick ? handleClick : undefined}
      onKeyDown={onClick ? handleKeyDown : undefined}
      role={onClick ? "button" : undefined}
      tabIndex={onClick ? 0 : undefined}
      className="p-5 animate-fade-in"
      style={{ animationDelay: `${Math.min(index * 50, 600)}ms` }}
    >
      {/* Header: name + tag + role + trend */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3 min-w-0">
          <div
            className="w-10 h-10 rounded-full flex items-center justify-center shrink-0 border-2"
            style={{
              borderColor: ROLE_COLORS[player.role] ?? "var(--color-border)",
              backgroundColor: "var(--color-surface-1)",
            }}
          >
            <Icon name="shield" size={18} className="text-[var(--color-text-secondary)]" />
          </div>
          <div className="min-w-0">
            <h3 className="text-base font-bold text-[var(--color-text-primary)] truncate">
              {player.name}
            </h3>
            <span className="text-xs text-[var(--color-text-tertiary)] tabular-nums">
              {player.tag}
            </span>
          </div>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          {hasTrend && <TrendIndicator trend={player.trend} />}
          <StatusBadge status={player.status} />
        </div>
      </div>

      {/* Role badge */}
      <div className="mb-4">
        <span
          className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-[var(--radius-pill)] text-xs font-medium"
          style={{
            color: ROLE_COLORS[player.role] ?? "var(--color-text-tertiary)",
            backgroundColor: "var(--color-surface-1)",
          }}
        >
          {ROLE_LABELS[player.role] ?? player.role}
        </span>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-3 gap-2 mb-4">
        <StatChip
          label="Hoje"
          value={`${player.attacks_today}/4`}
          icon="sword"
          color={player.attacks_today < 4 ? "red" : "green"}
        />
        <StatChip
          label="Total"
          value={`${player.attacks_total}/16`}
          color="default"
        />
        <StatChip
          label="Pontos"
          value={player.total_points}
          icon="trophy"
          color="yellow"
        />
      </div>

      {/* Card badges */}
      <div className="flex items-center gap-2 min-h-[28px]">
        {hasCards ? (
          <>
            <CardBadge type="yellow" count={player.yellow_cards} />
            <CardBadge type="red" count={player.red_cards} />
            <CardBadge type="black" count={player.black_cards} />
          </>
        ) : (
          <span className="text-xs text-[var(--color-text-tertiary)]">
            Sem cartões
          </span>
        )}
      </div>
    </Card>
  );
}
