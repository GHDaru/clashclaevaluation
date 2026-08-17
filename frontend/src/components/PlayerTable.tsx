import { useState, useMemo } from "react";
import type { PlayerStatusDTO } from "../types/domain";
import { Card } from "./Card";
import { StatusBadge } from "./StatusBadge";
import { CardBadge } from "./CardBadge";
import { TrendIndicator } from "./TrendIndicator";
import { Icon } from "./Icon";

interface PlayerTableProps {
  players: PlayerStatusDTO[];
  onPlayerClick?: (tag: string) => void;
}

type SortKey = "points" | "name" | "status" | "cards" | "attacks" | "attacks_today";
type SortDir = "asc" | "desc";

const STATUS_ORDER: Record<string, number> = { critical: 0, danger: 1, warning: 2, clean: 3 };

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

export function PlayerTable({ players, onPlayerClick }: PlayerTableProps) {
  const [sortKey, setSortKey] = useState<SortKey>("points");
  const [sortDir, setSortDir] = useState<SortDir>("desc");
  const [search, setSearch] = useState("");
  const [onlyWarPlayers, setOnlyWarPlayers] = useState(false);

  const filtered = useMemo(() => {
    let result = players;

    // Filter: only current war players (attacks_total > 0)
    if (onlyWarPlayers) {
      result = result.filter((p) => (p.attacks_total ?? 0) > 0);
    }

    // Filter: search by name
    if (search.trim()) {
      const q = search.trim().toLowerCase();
      result = result.filter(
        (p) => p.name.toLowerCase().includes(q) || p.tag.toLowerCase().includes(q)
      );
    }

    return result;
  }, [players, onlyWarPlayers, search]);

  const sorted = useMemo(() => {
    const arr = [...filtered];
    arr.sort((a, b) => {
      let cmp = 0;
      switch (sortKey) {
        case "points":
          cmp = (a.total_points ?? 0) - (b.total_points ?? 0);
          break;
        case "name":
          cmp = a.name.localeCompare(b.name, "pt-BR");
          break;
        case "status":
          cmp = (STATUS_ORDER[a.status] ?? 3) - (STATUS_ORDER[b.status] ?? 3);
          break;
        case "cards": {
          const aCards = (a.yellow_cards ?? 0) + (a.red_cards ?? 0) * 10 + (a.black_cards ?? 0) * 100;
          const bCards = (b.yellow_cards ?? 0) + (b.red_cards ?? 0) * 10 + (b.black_cards ?? 0) * 100;
          cmp = aCards - bCards;
          break;
        }
        case "attacks":
          cmp = (a.attacks_total ?? 0) - (b.attacks_total ?? 0);
          break;
        case "attacks_today":
          cmp = (a.attacks_today ?? 0) - (b.attacks_today ?? 0);
          break;
      }
      return sortDir === "desc" ? -cmp : cmp;
    });
    return arr;
  }, [filtered, sortKey, sortDir]);

  const toggleSort = (key: SortKey) => {
    if (key === sortKey) {
      setSortDir(sortDir === "asc" ? "desc" : "asc");
    } else {
      setSortKey(key);
      setSortDir(key === "name" ? "asc" : "desc");
    }
  };

  const SortIcon = ({ active }: { active: boolean }) =>
    active ? (
      <Icon name={sortDir === "asc" ? "chevron-down" : "chevron-up"} size={14} />
    ) : (
      <Icon name="chevron-down" size={14} className="opacity-30" />
    );

  return (
    <div className="space-y-3">
      {/* Toolbar */}
      <div className="flex flex-col sm:flex-row gap-3 sm:items-center sm:justify-between">
        <div className="flex items-center gap-2 flex-1 max-w-sm">
          <div className="relative flex-1">
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Buscar jogador..."
              className="w-full pl-9 pr-3 py-2 rounded-[var(--radius-sm)] bg-[var(--color-surface-1)] border border-[var(--color-border)] text-sm text-[var(--color-text-primary)] placeholder:text-[var(--color-text-tertiary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent transition-all"
            />
            <Icon
              name="search"
              size={16}
              className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--color-text-tertiary)]"
            />
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setOnlyWarPlayers(!onlyWarPlayers)}
            className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-[var(--radius-sm)] text-xs font-medium transition-all ${
              onlyWarPlayers
                ? "bg-[var(--color-primary)] text-white"
                : "bg-[var(--color-surface-1)] text-[var(--color-text-secondary)] border border-[var(--color-border)]"
            }`}
          >
            <Icon name="sword" size={14} />
            Só da guerra atual
          </button>
          <span className="text-xs text-[var(--color-text-tertiary)] tabular-nums">
            {sorted.length} / {players.length}
          </span>
        </div>
      </div>

      {/* Table */}
      <Card className="overflow-hidden p-0">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[var(--color-border)] bg-[var(--color-surface-1)]">
                <th
                  className="text-left px-4 py-2.5 font-semibold text-[var(--color-text-secondary)] cursor-pointer hover:text-[var(--color-text-primary)] transition-colors whitespace-nowrap"
                  onClick={() => toggleSort("name")}
                >
                  <span className="inline-flex items-center gap-1">
                    Jogador <SortIcon active={sortKey === "name"} />
                  </span>
                </th>
                <th
                  className="text-center px-3 py-2.5 font-semibold text-[var(--color-text-secondary)] cursor-pointer hover:text-[var(--color-text-primary)] transition-colors whitespace-nowrap"
                  onClick={() => toggleSort("attacks_today")}
                >
                  <span className="inline-flex items-center gap-1">
                    Hoje <SortIcon active={sortKey === "attacks_today"} />
                  </span>
                </th>
                <th
                  className="text-center px-3 py-2.5 font-semibold text-[var(--color-text-secondary)] cursor-pointer hover:text-[var(--color-text-primary)] transition-colors whitespace-nowrap"
                  onClick={() => toggleSort("attacks")}
                >
                  <span className="inline-flex items-center gap-1">
                    Total <SortIcon active={sortKey === "attacks"} />
                  </span>
                </th>
                <th
                  className="text-right px-3 py-2.5 font-semibold text-[var(--color-text-secondary)] cursor-pointer hover:text-[var(--color-text-primary)] transition-colors whitespace-nowrap"
                  onClick={() => toggleSort("points")}
                >
                  <span className="inline-flex items-center gap-1">
                    Pontos <SortIcon active={sortKey === "points"} />
                  </span>
                </th>
                <th
                  className="text-center px-3 py-2.5 font-semibold text-[var(--color-text-secondary)] cursor-pointer hover:text-[var(--color-text-primary)] transition-colors whitespace-nowrap"
                  onClick={() => toggleSort("cards")}
                >
                  <span className="inline-flex items-center gap-1">
                    Cartões <SortIcon active={sortKey === "cards"} />
                  </span>
                </th>
                <th
                  className="text-center px-3 py-2.5 font-semibold text-[var(--color-text-secondary)] cursor-pointer hover:text-[var(--color-text-primary)] transition-colors whitespace-nowrap"
                  onClick={() => toggleSort("status")}
                >
                  <span className="inline-flex items-center gap-1">
                    Status <SortIcon active={sortKey === "status"} />
                  </span>
                </th>
              </tr>
            </thead>
            <tbody>
              {sorted.length === 0 ? (
                <tr>
                  <td colSpan={6} className="text-center py-12 text-[var(--color-text-tertiary)]">
                    Nenhum jogador encontrado
                  </td>
                </tr>
              ) : (
                sorted.map((p, i) => {
                  const tagForClick = (p.tag ?? "").replace("#", "");
                  const hasCards =
                    (p.yellow_cards ?? 0) > 0 || (p.red_cards ?? 0) > 0 || (p.black_cards ?? 0) > 0;
                  const hasTrend = p.trend && p.trend !== "new";
                  return (
                    <tr
                      key={p.tag}
                      onClick={onPlayerClick ? () => onPlayerClick(tagForClick) : undefined}
                      className={`border-b border-[var(--color-border)] last:border-b-0 transition-colors ${
                        onPlayerClick ? "cursor-pointer hover:bg-[var(--color-surface-2)]" : ""
                      } ${i % 2 === 1 ? "bg-[var(--color-surface-0)]/50" : ""}`}
                    >
                      {/* Name + role + tag */}
                      <td className="px-4 py-2.5">
                        <div className="flex items-center gap-2.5 min-w-0">
                          <div
                            className="w-8 h-8 rounded-full flex items-center justify-center shrink-0 border-2"
                            style={{
                              borderColor: ROLE_COLORS[p.role] ?? "var(--color-border)",
                              backgroundColor: "var(--color-surface-1)",
                            }}
                          >
                            <Icon name="shield" size={14} className="text-[var(--color-text-secondary)]" />
                          </div>
                          <div className="min-w-0">
                            <div className="flex items-center gap-2">
                              <span className="font-medium text-[var(--color-text-primary)] truncate">
                                {p.name}
                              </span>
                              {hasTrend && <TrendIndicator trend={p.trend} />}
                            </div>
                            <span className="text-xs text-[var(--color-text-tertiary)] tabular-nums">
                              {ROLE_LABELS[p.role] ?? p.role} · {p.tag}
                            </span>
                          </div>
                        </div>
                      </td>
                      {/* Attacks today */}
                      <td className="text-center px-3 py-2.5">
                        <span
                          className={`tabular-nums font-medium ${
                            (p.attacks_today ?? 0) < 4
                              ? "text-[var(--color-danger)]"
                              : "text-[var(--color-success)]"
                          }`}
                        >
                          {p.attacks_today ?? 0}/4
                        </span>
                      </td>
                      {/* Attacks total */}
                      <td className="text-center px-3 py-2.5 tabular-nums text-[var(--color-text-secondary)]">
                        {p.attacks_total ?? 0}/16
                      </td>
                      {/* Points */}
                      <td className="text-right px-3 py-2.5 tabular-nums font-semibold text-[var(--color-accent)]">
                        {(p.total_points ?? 0).toLocaleString("pt-BR")}
                      </td>
                      {/* Cards */}
                      <td className="text-center px-3 py-2.5">
                        {hasCards ? (
                          <div className="inline-flex items-center gap-1">
                            <CardBadge type="yellow" count={p.yellow_cards} />
                            <CardBadge type="red" count={p.red_cards} />
                            <CardBadge type="black" count={p.black_cards} />
                          </div>
                        ) : (
                          <span className="text-xs text-[var(--color-text-tertiary)]">—</span>
                        )}
                      </td>
                      {/* Status */}
                      <td className="text-center px-3 py-2.5">
                        <StatusBadge status={p.status} />
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
