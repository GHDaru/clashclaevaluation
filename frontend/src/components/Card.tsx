import type { HTMLAttributes, ReactNode } from "react";

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  interactive?: boolean;
  children: ReactNode;
}

export function Card({ interactive = false, children, className = "", ...props }: CardProps) {
  return (
    <div
      className={`bg-[var(--color-surface-2)] border border-[var(--color-border)] rounded-[var(--radius-lg)] shadow-[var(--shadow-card)] ${
        interactive
          ? "cursor-pointer transition-transform duration-150 ease-[var(--ease-out)] hover:-translate-y-0.5 hover:border-[var(--color-border-strong)] hover:shadow-[var(--shadow-md)]"
          : ""
      } ${className}`}
      {...props}
    >
      {children}
    </div>
  );
}
