import { useState } from "react";
import { Card } from "../components/Card";
import { Button } from "../components/Button";
import { Icon } from "../components/Icon";

interface PlayerLookupProps {
  onSubmit: (tag: string) => void;
  onBack: () => void;
}

export default function PlayerLookup({ onSubmit, onBack }: PlayerLookupProps) {
  const [tag, setTag] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = () => {
    const cleaned = tag.trim().startsWith("#") ? tag.trim() : `#${tag.trim()}`;
    if (!cleaned || cleaned === "#") {
      setError("Insira um tag válido (ex: #ABC123)");
      return;
    }
    if (!/^#[A-Z0-9]+$/.test(cleaned)) {
      setError("Tag deve conter apenas letras maiúsculas e números");
      return;
    }
    setError("");
    onSubmit(cleaned.replace("#", ""));
  };

  return (
    <div className="max-w-md mx-auto py-12">
      <Card className="p-8 animate-fade-in">
        <div className="text-center mb-6">
          <div className="flex justify-center mb-4">
            <div className="w-14 h-14 rounded-full flex items-center justify-center border-2 border-[var(--color-accent)] bg-[var(--color-surface-1)]">
              <Icon name="shield" size={28} className="text-[var(--color-accent)]" />
            </div>
          </div>
          <h2 className="text-xl font-bold text-[var(--color-text-primary)] mb-2">
            Ver minha performance
          </h2>
          <p className="text-sm text-[var(--color-text-secondary)]">
            Insira seu tag de jogador do Clash Royale para ver seu histórico de guerras.
          </p>
        </div>

        <div className="space-y-3">
          <div className="relative">
            <input
              type="text"
              value={tag}
              onChange={(e) => setTag(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
              placeholder="#seu_tag"
              autoFocus
              className="w-full px-4 py-3 rounded-[var(--radius-sm)] bg-[var(--color-surface-1)] border border-[var(--color-border)] text-[var(--color-text-primary)] placeholder:text-[var(--color-text-tertiary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent transition-all tabular-nums uppercase"
            />
          </div>

          {error && (
            <p className="text-sm text-[var(--color-danger)] flex items-center gap-1.5">
              <Icon name="alert" size={14} />
              {error}
            </p>
          )}

          <Button
            variant="primary"
            size="md"
            iconLeft="search"
            onClick={handleSubmit}
            className="w-full"
          >
            Ver performance
          </Button>

          <button
            onClick={onBack}
            className="w-full text-sm text-[var(--color-text-tertiary)] hover:text-[var(--color-text-secondary)] transition-colors py-2"
          >
            Voltar
          </button>
        </div>
      </Card>
    </div>
  );
}
