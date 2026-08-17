import type { ClanStatusDTO } from "../types/domain";
import { PlayerTable } from "../components/PlayerTable";
import { WarProgressBar } from "../components/WarProgressBar";
import { Card } from "../components/Card";
import { StatChip } from "../components/StatChip";
import { Icon } from "../components/Icon";
import { Button } from "../components/Button";

interface Props {
  data: ClanStatusDTO;
  onPlayerClick?: (tag: string) => void;
}

export default function Dashboard({ data, onPlayerClick }: Props) {
  const players = data?.players ?? [];

  const statusCounts = players.reduce(
    (acc, p) => {
      acc[p.status] = (acc[p.status] ?? 0) + 1;
      return acc;
    },
    {} as Record<string, number>
  );

  const warPlayersCount = players.filter((p) => (p.attacks_total ?? 0) > 0).length;

  return (
    <div className="space-y-6">
      {/* War Status Banner */}
      <Card className="p-5">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-[var(--color-text-primary)]">
            Corrida do Rio
          </h2>
          {data.relaxed && (
            <span
              className="inline-flex items-center gap-1.5 px-3 py-1 rounded-[var(--radius-pill)] text-xs font-semibold"
              style={{
                backgroundColor: "var(--color-success-bg)",
                color: "var(--color-success)",
              }}
            >
              <Icon name="flag" size={12} />
              Relaxado
            </span>
          )}
        </div>
        {data?.war_active ? (
          <>
            <WarProgressBar currentDay={data.day ?? 0} relaxed={data?.relaxed ?? false} />
            <div className="flex items-center justify-center gap-4 sm:gap-6 mt-4 flex-wrap">
              <StatChip
                label="Dia"
                value={`${(data.day ?? 0) + 1}/4`}
                sublabel={data.day_label ?? ""}
                icon="calendar"
                color="blue"
              />
              <StatChip
                label="Posição"
                value={`${data.position ?? "—"}º`}
                sublabel={data.clans_count ? `de ${data.clans_count} clãs` : ""}
                icon="trophy"
                color="yellow"
              />
              <StatChip
                label="Fama Total"
                value={(data.total_fame ?? 0).toLocaleString("pt-BR")}
                color="green"
              />
              <StatChip
                label="Fama Hoje"
                value={(data.daily_fame ?? 0).toLocaleString("pt-BR")}
                icon="fire"
                color="red"
              />
            </div>
          </>
        ) : (
          <div className="text-center py-6">
            <Icon
              name="calendar"
              size={32}
              className="text-[var(--color-text-tertiary)] mx-auto mb-2"
            />
            <p className="text-sm text-[var(--color-text-secondary)]">
              Sem guerra ativa
            </p>
          </div>
        )}
      </Card>

      {/* Summary Stats */}
      {players.length > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <Card className="p-4 flex items-center justify-between">
            <StatChip label="Jogadores" value={players.length} icon="users" color="blue" />
          </Card>
          <Card className="p-4 flex items-center justify-between">
            <StatChip
              label="Na Guerra"
              value={warPlayersCount}
              icon="sword"
              color="green"
            />
          </Card>
          <Card className="p-4 flex items-center justify-between">
            <StatChip
              label="Críticos"
              value={statusCounts.critical ?? 0}
              icon="fire"
              color="red"
            />
          </Card>
          <Card className="p-4 flex items-center justify-between">
            <StatChip
              label="Alertas"
              value={(statusCounts.warning ?? 0) + (statusCounts.danger ?? 0)}
              icon="alert"
              color="yellow"
            />
          </Card>
        </div>
      )}

      {/* Player Table */}
      {players.length > 0 ? (
        <PlayerTable players={players} onPlayerClick={onPlayerClick} />
      ) : (
        <Card className="p-12 text-center">
          <div className="flex flex-col items-center gap-4">
            <Icon
              name="users"
              size={48}
              className="text-[var(--color-text-tertiary)]"
            />
            <div>
              <h3 className="text-base font-bold text-[var(--color-text-primary)] mb-1">
                Nenhum jogador encontrado
              </h3>
              <p className="text-sm text-[var(--color-text-secondary)]">
                Clique em "Avaliar" para coletar dados da API.
              </p>
            </div>
            {onPlayerClick && (
              <Button variant="primary" iconLeft="bolt">
                Avaliar Clã
              </Button>
            )}
          </div>
        </Card>
      )}
    </div>
  );
}
