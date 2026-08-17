import { useState } from "react";
import { Card } from "../components/Card";
import { Button } from "../components/Button";
import { Icon } from "../components/Icon";
import { Logo } from "../components/Logo";

interface LandingProps {
  onClanView: (clanTag: string) => void;
  onPlayerView: (playerTag: string) => void;
}

const FEATURES = [
  {
    icon: "card-yellow" as const,
    title: "Sistema de Cartões",
    desc: "Amarelo para falta de ataque, vermelho para acúmulo, preto para expulsão. Automático e configurável.",
    color: "var(--color-card-yellow)",
    bg: "var(--color-card-yellow-bg)",
  },
  {
    icon: "trend-up" as const,
    title: "Recência & Histórico",
    desc: "Desempenho nas últimas N semanas pesa mais. Tendência de melhora ou declínio por jogador.",
    color: "var(--color-success)",
    bg: "var(--color-success-bg)",
  },
  {
    icon: "flag" as const,
    title: "Relaxamento de Regras",
    desc: "Clã garantiu 1º lugar? Domingo não gera cartão. Critérios configuráveis pelo líder.",
    color: "var(--color-accent)",
    bg: "rgba(245, 166, 35, 0.12)",
  },
];

export default function Landing({ onClanView, onPlayerView }: LandingProps) {
  const [clanTag, setClanTag] = useState("");
  const [playerTag, setPlayerTag] = useState("");
  const [clanError, setClanError] = useState("");
  const [playerError, setPlayerError] = useState("");

  const handleClanSubmit = () => {
    const cleaned = clanTag.trim().startsWith("#") ? clanTag.trim() : `#${clanTag.trim()}`;
    if (!cleaned || cleaned === "#") {
      setClanError("Insira um tag válido (ex: #QPUJC0CG)");
      return;
    }
    if (!/^#[A-Z0-9]+$/.test(cleaned)) {
      setClanError("Tag deve conter apenas letras maiúsculas e números");
      return;
    }
    setClanError("");
    onClanView(cleaned.replace("#", ""));
  };

  const handlePlayerSubmit = () => {
    const cleaned = playerTag.trim().startsWith("#") ? playerTag.trim() : `#${playerTag.trim()}`;
    if (!cleaned || cleaned === "#") {
      setPlayerError("Insira um tag válido (ex: #ABC123)");
      return;
    }
    if (!/^#[A-Z0-9]+$/.test(cleaned)) {
      setPlayerError("Tag deve conter apenas letras maiúsculas e números");
      return;
    }
    setPlayerError("");
    onPlayerView(cleaned.replace("#", ""));
  };

  return (
    <div className="space-y-12 py-8">
      {/* Hero */}
      <section className="text-center space-y-6 animate-fade-in">
        <div className="flex justify-center mb-4">
          <Logo size={72} />
        </div>
        <h1 className="text-4xl font-bold text-[var(--color-text-primary)] tracking-tight">
          ClashClanEvaluation
        </h1>
        <p className="text-lg text-[var(--color-text-secondary)] max-w-xl mx-auto">
          Sistema de avaliação de participação em{" "}
          <span className="text-[var(--color-accent)] font-semibold">
            Guerras de Clãs
          </span>{" "}
          (River Race / Corrida do Rio).
        </p>
        <p className="text-sm text-[var(--color-text-tertiary)] max-w-xl mx-auto">
          Rastreia ataques, atribui cartões, calcula tendências e ajuda líderes a decidir
          sobre permanência, advertências e expulsões.
        </p>
      </section>

      {/* Two Input Options */}
      <section className="grid md:grid-cols-2 gap-4 max-w-3xl mx-auto">
        {/* Clan Tag Input */}
        <Card className="p-6 animate-fade-in">
          <div className="flex items-center gap-3 mb-4">
            <div
              className="w-10 h-10 rounded-[var(--radius-md)] flex items-center justify-center"
              style={{ backgroundColor: "var(--color-primary-bg)", color: "var(--color-primary)" }}
            >
              <Icon name="users" size={20} />
            </div>
            <div>
              <h3 className="text-base font-bold text-[var(--color-text-primary)]">
                Ver dados do Clã
              </h3>
              <p className="text-xs text-[var(--color-text-tertiary)]">
                Análise completa do clã
              </p>
            </div>
          </div>
          <div className="space-y-2">
            <input
              type="text"
              value={clanTag}
              onChange={(e) => setClanTag(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleClanSubmit()}
              placeholder="#tag_do_cla"
              autoFocus
              className="w-full px-4 py-2.5 rounded-[var(--radius-sm)] bg-[var(--color-surface-1)] border border-[var(--color-border)] text-sm text-[var(--color-text-primary)] placeholder:text-[var(--color-text-tertiary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent transition-all tabular-nums uppercase"
            />
            {clanError && (
              <p className="text-xs text-[var(--color-danger)] flex items-center gap-1">
                <Icon name="alert" size={12} />
                {clanError}
              </p>
            )}
            <Button
              variant="primary"
              size="md"
              iconLeft="search"
              onClick={handleClanSubmit}
              className="w-full"
            >
              Analisar Clã
            </Button>
          </div>
        </Card>

        {/* Player Tag Input */}
        <Card className="p-6 animate-fade-in" style={{ animationDelay: "100ms" }}>
          <div className="flex items-center gap-3 mb-4">
            <div
              className="w-10 h-10 rounded-[var(--radius-md)] flex items-center justify-center"
              style={{ backgroundColor: "var(--color-accent-bg)", color: "var(--color-accent)" }}
            >
              <Icon name="shield" size={20} />
            </div>
            <div>
              <h3 className="text-base font-bold text-[var(--color-text-primary)]">
                Ver minha performance
              </h3>
              <p className="text-xs text-[var(--color-text-tertiary)]">
                Histórico individual de guerras
              </p>
            </div>
          </div>
          <div className="space-y-2">
            <input
              type="text"
              value={playerTag}
              onChange={(e) => setPlayerTag(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handlePlayerSubmit()}
              placeholder="#seu_tag"
              className="w-full px-4 py-2.5 rounded-[var(--radius-sm)] bg-[var(--color-surface-1)] border border-[var(--color-border)] text-sm text-[var(--color-text-primary)] placeholder:text-[var(--color-text-tertiary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent transition-all tabular-nums uppercase"
            />
            {playerError && (
              <p className="text-xs text-[var(--color-danger)] flex items-center gap-1">
                <Icon name="alert" size={12} />
                {playerError}
              </p>
            )}
            <Button
              variant="secondary"
              size="md"
              iconLeft="search"
              onClick={handlePlayerSubmit}
              className="w-full"
            >
              Ver performance
            </Button>
          </div>
        </Card>
      </section>

      {/* Feature Highlights */}
      <section className="grid md:grid-cols-3 gap-4 max-w-4xl mx-auto">
        {FEATURES.map((f, i) => (
          <Card
            key={f.title}
            className="p-6 animate-fade-in"
            style={{ animationDelay: `${i * 100}ms` }}
          >
            <div className="flex items-center gap-3 mb-3">
              <div
                className="w-10 h-10 rounded-[var(--radius-md)] flex items-center justify-center shrink-0"
                style={{ backgroundColor: f.bg, color: f.color }}
              >
                <Icon name={f.icon} size={20} />
              </div>
              <h3 className="text-base font-bold text-[var(--color-text-primary)]">
                {f.title}
              </h3>
            </div>
            <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed">
              {f.desc}
            </p>
          </Card>
        ))}
      </section>

      {/* War focus banner */}
      <section className="max-w-4xl mx-auto">
        <Card className="p-6">
          <div className="flex items-start gap-4">
            <div className="shrink-0">
              <Icon name="sword" size={32} className="text-[var(--color-primary)]" />
            </div>
            <div>
              <h3 className="text-base font-bold text-[var(--color-text-primary)] mb-1">
                Focado em Guerra
              </h3>
              <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed">
                A guerra acontece de quinta a domingo (4 dias de batalha). Cada jogador tem 4
                ataques por dia usando 4 decks diferentes. O sistema coleta dados da API oficial
                do Clash Royale e avalia quem cumpriu e quem faltou.
              </p>
            </div>
          </div>
        </Card>
      </section>
    </div>
  );
}
