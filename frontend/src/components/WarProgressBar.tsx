import { Icon } from "./Icon";

interface WarProgressBarProps {
  currentDay: number; // 0-3
  relaxed: boolean;
}

const DAYS = ["Qui", "Sex", "Sáb", "Dom"];

export function WarProgressBar({ currentDay, relaxed }: WarProgressBarProps) {
  return (
    <div
      className="flex gap-1.5"
      role="progressbar"
      aria-valuenow={currentDay + 1}
      aria-valuemin={1}
      aria-valuemax={4}
    >
      {DAYS.map((day, i) => {
        const isPast = i < currentDay;
        const isCurrent = i === currentDay;
        const isFuture = i > currentDay;
        const isRelaxedDay = relaxed && i === 3;

        return (
          <div
            key={day}
            className={`flex-1 flex flex-col items-center gap-1.5 py-2.5 px-2 rounded-[var(--radius-md)] transition-all duration-300 ${
              isCurrent
                ? "bg-[var(--color-primary)] text-white shadow-[var(--shadow-glow-blue)]"
                : isPast
                  ? "bg-[var(--color-surface-3)] text-[var(--color-text-secondary)]"
                  : "bg-[var(--color-surface-1)] text-[var(--color-text-tertiary)]"
            }`}
          >
            <span className="text-xs font-semibold">{day}</span>
            <div className="flex items-center justify-center">
              {isPast && <Icon name="check" size={16} />}
              {isCurrent && (
                <span className="w-2 h-2 rounded-full bg-white animate-pulse" />
              )}
              {isFuture && isRelaxedDay && <Icon name="flag" size={14} />}
              {isFuture && !isRelaxedDay && (
                <span className="w-1.5 h-1.5 rounded-full bg-current opacity-40" />
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
