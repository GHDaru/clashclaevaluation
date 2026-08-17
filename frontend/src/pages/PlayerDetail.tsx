import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";
import type { PlayerHistoryDTO, PlayerWarEntry } from "../types/domain";
import { Card } from "../components/Card";
import { StatChip } from "../components/StatChip";
import { CardBadge } from "../components/CardBadge";
import { StatusBadge } from "../components/StatusBadge";
import { TrendIndicator } from "../components/TrendIndicator";
import { Button } from "../components/Button";
import { Icon } from "../components/Icon";
import { Skeleton } from "../components/Skeleton";

interface Props {
  playerTag: string;
  onBack: () => void;
}

const ROLE_LABELS: Record<string, string> = {
  leader: "Líder",
  coLeader: "Co-Líder",
  elder: "Veterano",
  member: "Membro",
};

const STATUS_MAP: Record<string, "clean" | "warning" | "danger" | "critical"> = {
  clean: "clean",
  warning: "warning",
  danger: "danger",
  critical: "critical",
};

function WarMiniCard({ war, index }: { war: PlayerWarEntry; index: number }) {
  const status = war.status ? STATUS_MAP[war.status] ?? "clean" : "clean";
  return (
    <Card className="p-3 flex items-center justify-between gap-3">
      <div className="flex items-center gap-2">
        <span className="text-xs text-[var(--color-text-tertiary)] tabular-nums font-medium">
          #{index + 1}
        </span>
        <StatusBadge status={status} />
      </div>
      <div className="flex items-center gap-1.5">
        <CardBadge type="yellow" count={war.yellow_cards ?? 0} />
        <CardBadge type="red" count={war.red_cards ?? 0} />
        <CardBadge type="black" count={war.black_cards ?? 0} />
      </div>
      <span className="text-sm tabular-nums text-[var(--color-text-secondary)] font-medium">
        {(war.total_points ?? 0).toLocaleString("pt-BR")}
      </span>
    </Card>
  );
}

export default function PlayerDetail({ playerTag, onBack }: Props) {
  const [expanded, setExpanded] = useState(false);

  const { data, isLoading, error } = useQuery<PlayerHistoryDTO>({
    queryKey: ["playerHistory", playerTag, expanded],
    queryFn: () => api.getPlayerHistory(playerTag, expanded),
  });

  if (isLoading) {
    return (
      <div className="max-w-3xl mx-auto space-y-4">
        <Skeleton className="h-12 w-full rounded-[var(--radius-lg)]" />
        <Skeleton className="h-40 w-full rounded-[var(--radius-lg)]" />
        <Skeleton className="h-40 w-full rounded-[var(--radius-lg)]" />
        <Skeleton className="h-40 w-full rounded-[var(--radius-lg)]" />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="max-w-2xl mx-auto">
        <Card className="p-8 text-center">
          <Icon name="alert" size={40} className="text-[var(--color-danger)] mx-auto mb-3" />
          <p className="text-[var(--color-text-secondary)] mb-4">
            Erro ao carregar dados do jogador.
          </p>
          <Button variant="ghost" iconLeft="chevron-left" onClick={onBack}>
            Voltar ao painel
          </Button>
        </Card>
      </div>
    );
  }

  const dateFormatter = new Intl.DateTimeFormat("pt-BR", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });

  return (
    <div className="max-w-3xl mx-auto space-y-5">
      {/* Player Header */}
      <Card className="p-5">
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-full flex items-center justify-center bg-[var(--color-surface-1)] border-2 border-[var(--color-accent)]">
            <Icon name="shield" size={24} className="text-[var(--color-accent)]" />
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-1">
              <h1 className="text-2xl font-bold text-[var(--color-text-primary)]">
                {data.name}
              </h1>
              <span className="text-sm text-[var(--color-text-tertiary)] tabular-nums">
                {data.tag}
              </span>
            </div>
            <div className="flex items-center gap-3">
              <span
                className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-[var(--radius-pill)] text-xs font-medium"
                style={{
                  color: "var(--color-accent)",
                  backgroundColor: "var(--color-surface-1)",
                }}
              >
                {ROLE_LABELS[data.role] ?? data.role}
              </span>
              {data.first_seen && (
                <span className="text-xs text-[var(--color-text-tertiary)]">
                  Membro desde {dateFormatter.format(new Date(data.first_seen))}
                </span>
              )}
            </div>
          </div>
        </div>
      </Card>

      {/* Current War */}
      <Card className="p-5">
        <div className="flex items-center gap-2 mb-2">
          <Icon name="bolt" size={18} className="text-[var(--color-accent)]" />
          <h2 className="text-lg font-bold text-[var(--color-text-primary)]">
            Guerra Atual
          </h2>
        </div>
        <p className="text-xs text-[var(--color-text-tertiary)] mb-4 leading-relaxed">
          A guerra dura 4 dias (qui-dom). Cada jogador tem 4 ataques por dia. Cartão amarelo = faltou ataque no dia.
          Vermelho = acúmulo de amarelos. Preto = candidato à expulsão.
        </p>
        {data.current_war ? (
          <>
            <div className="grid grid-cols-4 gap-3 mb-4">
              <StatChip
                label="Amarelos"
                value={data.current_war.yellow_cards ?? 0}
                icon="card-yellow"
                color="yellow"
                size="lg"
              />
              <StatChip
                label="Vermelhos"
                value={data.current_war.red_cards ?? 0}
                icon="card-red"
                color="red"
                size="lg"
              />
              <StatChip
                label="Pretos"
                value={data.current_war.black_cards ?? 0}
                icon="card-black"
                color="black"
                size="lg"
              />
              <StatChip
                label="Pontos"
                value={(data.current_war.total_points ?? 0).toLocaleString("pt-BR")}
                icon="trophy"
                color="green"
                size="lg"
              />
            </div>
            <div className="flex justify-center">
              <StatusBadge
                status={
                  data.current_war.status
                    ? STATUS_MAP[data.current_war.status] ?? "clean"
                    : "clean"
                }
              />
            </div>
          </>
        ) : (
          <p className="text-sm text-[var(--color-text-secondary)] text-center py-4">
            Sem dados da guerra atual.
          </p>
        )}
      </Card>

      {/* Recency */}
      <Card className="p-5">
        <div className="flex items-center gap-2 mb-2">
          <Icon name="trophy" size={18} className="text-[var(--color-accent)]" />
          <h2 className="text-lg font-bold text-[var(--color-text-primary)]">
            Recência — Corrida dos Campeões
          </h2>
        </div>
        <p className="text-xs text-[var(--color-text-tertiary)] mb-4 leading-relaxed">
          Últimas 4 semanas. A tendência compara cartões amarelos recentes vs anteriores:
          melhorando (menos faltas), estável ou declinando (mais faltas).
        </p>
        <div className="flex items-center gap-3 mb-4">
          <span className="text-sm text-[var(--color-text-secondary)]">Tendência:</span>
          <TrendIndicator
            trend={(data.recency.trend as "improving" | "stable" | "declining" | "new") ?? "stable"}
            showLabel
          />
        </div>
        {data.recency.wars && data.recency.wars.length > 0 ? (
          <div className="space-y-2">
            {data.recency.wars.map((w, i) => (
              <WarMiniCard key={i} war={w} index={i} />
            ))}
          </div>
        ) : (
          <p className="text-sm text-[var(--color-text-secondary)] text-center py-4">
            Sem dados recentes.
          </p>
        )}
      </Card>

      {/* Full History */}
      <Card className="p-5">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Icon name="calendar" size={18} className="text-[var(--color-accent)]" />
            <h2 className="text-lg font-bold text-[var(--color-text-primary)]">
              Histórico {expanded ? "(3 meses)" : "(4 semanas)"}
            </h2>
          </div>
          <Button
            variant="ghost"
            size="sm"
            iconRight="chevron-down"
            onClick={() => setExpanded(!expanded)}
          >
            {expanded ? "Recolher" : "Expandir"}
          </Button>
        </div>
        {data.history.length > 0 ? (
          <div className="space-y-2">
            {data.history.map((w, i) => (
              <WarMiniCard key={i} war={w} index={i} />
            ))}
          </div>
        ) : (
          <p className="text-sm text-[var(--color-text-secondary)] text-center py-4">
            Sem histórico disponível.
          </p>
        )}
      </Card>
    </div>
  );
}
