interface SkeletonProps {
  className?: string;
}

export function Skeleton({ className = "" }: SkeletonProps) {
  return <div className={`skeleton-shimmer rounded-[var(--radius-sm)] ${className}`} />;
}

export function SkeletonCard() {
  return (
    <div className="bg-[var(--color-surface-2)] border border-[var(--color-border)] rounded-[var(--radius-lg)] p-5 shadow-[var(--shadow-card)]">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <Skeleton className="w-10 h-10 rounded-full" />
          <div className="space-y-2">
            <Skeleton className="w-32 h-4" />
            <Skeleton className="w-20 h-3" />
          </div>
        </div>
        <Skeleton className="w-16 h-6 rounded-full" />
      </div>
      <div className="grid grid-cols-3 gap-3 mb-4">
        <Skeleton className="h-12 rounded-[var(--radius-md)]" />
        <Skeleton className="h-12 rounded-[var(--radius-md)]" />
        <Skeleton className="h-12 rounded-[var(--radius-md)]" />
      </div>
      <div className="flex gap-2">
        <Skeleton className="w-16 h-7 rounded-[var(--radius-sm)]" />
        <Skeleton className="w-16 h-7 rounded-[var(--radius-sm)]" />
      </div>
    </div>
  );
}
