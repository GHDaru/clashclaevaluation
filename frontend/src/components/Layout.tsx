import type { ReactNode } from "react";
import { Logo } from "./Logo";
import { Button } from "./Button";

interface LayoutProps {
  children: ReactNode;
  onEvaluate: () => void;
  onConfig: () => void;
  evaluating: boolean;
  showConfig: boolean;
  onBack?: () => void;
  backLabel?: string;
  onHome?: () => void;
}

export function Layout({
  children,
  onEvaluate,
  onConfig,
  evaluating,
  showConfig,
  onBack,
  backLabel = "Voltar",
  onHome,
}: LayoutProps) {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="sticky top-0 z-20 backdrop-blur-md bg-[var(--color-surface-0)]/80 border-b border-[var(--color-border)]">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          <div
            className="flex items-center gap-3 cursor-pointer hover:opacity-80 transition-opacity"
            onClick={onHome}
            role={onHome ? "button" : undefined}
            tabIndex={onHome ? 0 : undefined}
            onKeyDown={onHome ? (e) => (e.key === "Enter" || e.key === " ") && onHome() : undefined}
          >
            <Logo size={36} />
            <div>
              <h1 className="text-lg font-bold text-[var(--color-text-primary)] leading-none">
                ClashClanEval
              </h1>
              <span className="text-xs text-[var(--color-text-tertiary)]">
                Clan Evaluation
              </span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {onBack && (
              <Button
                variant="ghost"
                size="sm"
                iconLeft="chevron-left"
                onClick={onBack}
              >
                <span className="hidden sm:inline">{backLabel}</span>
              </Button>
            )}
            {!showConfig && (
              <Button
                variant="primary"
                size="sm"
                iconLeft="bolt"
                onClick={onEvaluate}
                loading={evaluating}
              >
                <span className="hidden sm:inline">Avaliar</span>
              </Button>
            )}
            {!showConfig && (
              <Button
                variant="secondary"
                size="sm"
                iconLeft="cog"
                onClick={onConfig}
              >
                <span className="hidden sm:inline">Config</span>
              </Button>
            )}
          </div>
        </div>
      </header>
      <main className="flex-1 max-w-6xl mx-auto w-full px-4 py-6">
        {children}
      </main>
      <footer className="border-t border-[var(--color-border)] mt-auto">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between flex-wrap gap-2">
          <p className="text-xs text-[var(--color-text-tertiary)]">
            Desenvolvido por{" "}
            <a
              href="https://ghdaru.com.br"
              target="_blank"
              rel="noopener noreferrer"
              className="text-[var(--color-accent)] hover:text-[var(--color-accent-hover)] font-medium transition-colors"
            >
              GHDaru Tecnologia
            </a>
          </p>
          <p className="text-xs text-[var(--color-text-tertiary)]">
            ClashClanEvaluation © {new Date().getFullYear()}
          </p>
        </div>
      </footer>
    </div>
  );
}
