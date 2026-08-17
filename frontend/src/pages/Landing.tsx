import { Card } from "../components/Card";
import { Button } from "../components/Button";
import { Icon } from "../components/Icon";
import { Logo } from "../components/Logo";

interface LandingProps {
  onClanView: () => void;
  onPlayerView: () => void;
}

const FEATURES = [
  {
    icon: "card-yellow" as const,
    title: "Sistema de Cartões",
    desc: "Amarelo para falta de ataque, vermelho por acúmulo, preto para expulsão. Automático e configurável.",
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
        <p className="text-lg text-[var(--color-text-secondary)] max-w-2xl mx-auto">
          Sistema de avaliação de participação de membros do clã em{" "}
          <span className="text-[var(--color-accent)] font-semibold">
            Guerras de Clãs
          </span>{" "}
          (River Race / Corrida do Rio).
        </p>
        <p className="text-sm text-[var(--color-text-tertiary)] max-w-xl mx-auto">
          Rastreia ataques, atribui cartões, calcula tendências e ajuda líderes a decidir sobre
          permanência, advertências e expulsões.
        </p>

        {/* CTAs */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
          <Button
            variant="primary"
            size="md"
            iconLeft="users"
            onClick={onClanView}
            className="w-full sm:w-auto"
          >
            Ver dados do Clã
          </Button>
          <Button
            variant="secondary"
            size="md"
            iconLeft="shield"
            onClick={onPlayerView}
            className="w-full sm:w-auto"
          >
            Ver minha performance
          </Button>
        </div>
      </section>

      {/* Feature Highlights */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-4">
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
      <section>
        <Card className="p-6">
          <div className="flex items-start gap-4">
            <div className="shrink-0">
              <Icon name="sword" size={32} className="text-[var(--color-primary)]" />
            </div>
            <div>
              <h3 className="text-base font-bold text-[var(--color-text-primary)] mb-1">
                Focado em Guerra
              </h3>
              <p className="text-sm text-[var(--color-text-secondary)]">
                A guerra acontece de quinta a domingo (4 dias de batalha). Cada jogador tem 4 ataques
                por dia usando 4 decks diferentes. O sistema coleta dados da API oficial do Clash
                Royale e avalia quem cumpriu e quem faltou.
              </p>
            </div>
          </div>
        </Card>
      </section>
    </div>
  );
}
