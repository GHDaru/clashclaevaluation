interface LogoProps {
  size?: number;
}

export function Logo({ size = 32 }: LogoProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 40 40"
      fill="none"
      aria-hidden="true"
    >
      {/* Shield outline */}
      <path
        d="M20 3 6 8v12c0 8 5.5 14 14 18 8.5-4 14-10 14-18V8L20 3Z"
        fill="var(--color-surface-3)"
        stroke="var(--color-accent)"
        strokeWidth="1.5"
      />
      {/* Crown */}
      <path
        d="M12 14l3 4 5-6 5 6 3-4v6H12v-6Z"
        fill="var(--color-accent)"
      />
      {/* Sword cross */}
      <rect x="19" y="16" width="2" height="14" fill="var(--color-primary)" rx="1" />
      <rect x="14" y="21" width="12" height="2" fill="var(--color-primary)" rx="1" />
      <circle cx="20" cy="22" r="2.5" fill="var(--color-accent)" />
    </svg>
  );
}
