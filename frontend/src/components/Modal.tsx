import { useEffect, type ReactNode } from "react";
import { Icon } from "./Icon";
import { Button } from "./Button";

interface ModalProps {
  open: boolean;
  title: string;
  children: ReactNode;
  confirmLabel?: string;
  cancelLabel?: string;
  destructive?: boolean;
  onConfirm?: () => void;
  onCancel: () => void;
}

export function Modal({
  open,
  title,
  children,
  confirmLabel = "Confirmar",
  cancelLabel = "Cancelar",
  destructive = false,
  onConfirm,
  onCancel,
}: ModalProps) {
  useEffect(() => {
    if (!open) return;
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") onCancel();
    };
    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, [open, onCancel]);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-40 flex items-center justify-center p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
    >
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm animate-fade-in"
        onClick={onCancel}
      />
      <div className="relative bg-[var(--color-surface-3)] border border-[var(--color-border-strong)] rounded-[var(--radius-lg)] shadow-[var(--shadow-lg)] max-w-md w-full p-6 animate-scale-in">
        <div className="flex items-center justify-between mb-4">
          <h2 id="modal-title" className="text-lg font-bold text-[var(--color-text-primary)]">
            {title}
          </h2>
          <button
            onClick={onCancel}
            className="text-[var(--color-text-tertiary)] hover:text-[var(--color-text-primary)] transition-colors touch-manipulation focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-primary)] rounded"
            aria-label="Fechar"
          >
            <Icon name="x" size={20} />
          </button>
        </div>
        <div className="text-sm text-[var(--color-text-secondary)] mb-6">{children}</div>
        <div className="flex justify-end gap-3">
          <Button variant="ghost" onClick={onCancel}>
            {cancelLabel}
          </Button>
          <Button variant={destructive ? "danger" : "primary"} onClick={onConfirm}>
            {confirmLabel}
          </Button>
        </div>
      </div>
    </div>
  );
}
