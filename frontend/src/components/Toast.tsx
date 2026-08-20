import {
  createContext,
  useCallback,
  useContext,
  useState,
  type ReactNode,
} from "react";
import { Icon, type IconName } from "./Icon";

type ToastType = "success" | "error" | "info" | "warning";

interface ToastItem {
  id: number;
  type: ToastType;
  message: string;
}

interface ToastContextValue {
  show: (type: ToastType, message: string) => void;
  success: (message: string) => void;
  error: (message: string) => void;
  info: (message: string) => void;
  warning: (message: string) => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

const TOAST_CONFIG: Record<ToastType, { icon: IconName; color: string; bg: string }> = {
  success: { icon: "check", color: "var(--color-success)", bg: "var(--color-success-bg)" },
  error: { icon: "alert", color: "var(--color-danger)", bg: "var(--color-danger-bg)" },
  info: { icon: "info", color: "var(--color-info)", bg: "var(--color-info-bg)" },
  warning: { icon: "alert", color: "var(--color-warning)", bg: "var(--color-warning-bg)" },
};

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<ToastItem[]>([]);

  const show = useCallback((type: ToastType, message: string) => {
    const id = Date.now() + Math.random();
    setToasts((prev) => [...prev, { id, type, message }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4000);
  }, []);

  const value: ToastContextValue = {
    show,
    success: (msg) => show("success", msg),
    error: (msg) => show("error", msg),
    info: (msg) => show("info", msg),
    warning: (msg) => show("warning", msg),
  };

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div
        className="fixed bottom-4 right-4 z-50 flex flex-col gap-2"
        aria-live="polite"
        aria-atomic="true"
      >
        {toasts.map((toast) => {
          const cfg = TOAST_CONFIG[toast.type];
          return (
            <div
              key={toast.id}
              className="flex items-center gap-3 px-4 py-3 rounded-[var(--radius-md)] shadow-[var(--shadow-lg)] border border-[var(--color-border)] animate-slide-in-right min-w-[280px]"
              style={{ backgroundColor: "var(--color-surface-3)", color: cfg.color }}
              role={toast.type === "error" ? "alert" : "status"}
            >
              <Icon name={cfg.icon} size={18} />
              <span className="text-sm font-medium text-[var(--color-text-primary)] flex-1">
                {toast.message}
              </span>
            </div>
          );
        })}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error("useToast must be used within ToastProvider");
  return ctx;
}
