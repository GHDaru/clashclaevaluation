import type { SVGProps } from "react";

export type IconName =
  | "sword"
  | "trophy"
  | "shield"
  | "cog"
  | "bolt"
  | "chevron-left"
  | "chevron-down"
  | "chevron-right"
  | "chevron-up"
  | "check"
  | "x"
  | "alert"
  | "fire"
  | "flag"
  | "trend-up"
  | "trend-flat"
  | "trend-down"
  | "sparkle"
  | "card-yellow"
  | "card-red"
  | "card-black"
  | "users"
  | "calendar"
  | "info"
  | "search";

interface IconProps extends SVGProps<SVGSVGElement> {
  name: IconName;
  size?: number;
}

const PATHS: Record<IconName, React.ReactNode> = {
  sword: <path d="M14.5 2.5 21 9l-2 2-3.5-3.5L8 15l-4 5 1 1 5-4 7.5-7.5L14 6l2-2-1.5-1.5Z" />,
  trophy: (
    <>
      <path d="M6 4h12v2a6 6 0 0 1-12 0V4Z" />
      <path d="M8 4H4v2a4 4 0 0 0 4 4" />
      <path d="M16 4h4v2a4 4 0 0 1-4 4" />
      <path d="M10 16h4l1 4H9l1-4Z" />
    </>
  ),
  shield: <path d="M12 2 4 5v6c0 5 3.5 8.5 8 11 4.5-2.5 8-6 8-11V5l-8-3Z" />,
  cog: (
    <>
      <circle cx="12" cy="12" r="3" />
      <path d="M12 2v3M12 19v3M22 12h-3M5 12H2M19.07 4.93l-2.12 2.12M7.05 16.95l-2.12 2.12M19.07 19.07l-2.12-2.12M7.05 7.05 4.93 4.93" />
    </>
  ),
  bolt: <path d="M13 2 4 14h7l-2 8 9-12h-7l2-8Z" />,
  "chevron-left": <path d="M15 6 9 12l6 6" />,
  "chevron-down": <path d="M6 9 12 15l6-6" />,
  "chevron-right": <path d="M9 6 15 12l-6 6" />,
  "chevron-up": <path d="M6 15 12 9l6 6" />,
  check: <path d="M5 12 10 17 19 7" />,
  x: <path d="M6 6 18 18M18 6 6 18" />,
  alert: (
    <>
      <path d="M12 3 2 20h20L12 3Z" />
      <path d="M12 10v4M12 17v.5" />
    </>
  ),
  fire: <path d="M12 2c1 3-1 5-2 7-1 2-2 4-2 6a6 6 0 0 0 12 0c0-2-1-4-2-5 0 1-1 2-2 2 1-3-1-7-4-10Z" />,
  flag: <path d="M5 3v18M5 4h12l-2 4 2 4H5" />,
  "trend-up": <path d="M3 17 10 10l4 4 7-7M17 7h4v4" />,
  "trend-flat": <path d="M3 12h18" />,
  "trend-down": <path d="M3 7 10 14l4-4 7 7M17 17h4v-4" />,
  sparkle: <path d="M12 3l1.5 5.5L19 10l-5.5 1.5L12 17l-1.5-5.5L5 10l5.5-1.5L12 3Z" />,
  "card-yellow": <rect x="4" y="3" width="16" height="18" rx="2" />,
  "card-red": <rect x="4" y="3" width="16" height="18" rx="2" />,
  "card-black": <rect x="4" y="3" width="16" height="18" rx="2" />,
  users: (
    <>
      <circle cx="9" cy="8" r="3" />
      <path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6" />
      <circle cx="17" cy="9" r="2.5" />
      <path d="M15 20c0-2.5 2-4.5 4.5-4.5S24 17.5 24 20" />
    </>
  ),
  calendar: (
    <>
      <rect x="3" y="5" width="18" height="16" rx="2" />
      <path d="M3 9h18M8 3v4M16 3v4" />
    </>
  ),
  info: (
    <>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 11v5M12 8v.5" />
    </>
  ),
  search: (
    <>
      <circle cx="11" cy="11" r="7" />
      <path d="M21 21l-4.35-4.35" />
    </>
  ),
};

const FILLED_ICONS: IconName[] = ["card-yellow", "card-red", "card-black", "bolt", "fire", "flag", "sparkle"];

export function Icon({ name, size = 20, className, ...props }: IconProps) {
  const filled = FILLED_ICONS.includes(name);
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill={filled ? "currentColor" : "none"}
      stroke={filled ? "none" : "currentColor"}
      strokeWidth={filled ? 0 : 2}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      className={className}
      {...props}
    >
      {PATHS[name]}
    </svg>
  );
}
