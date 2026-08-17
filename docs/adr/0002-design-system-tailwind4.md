# ADR 0002 — Design System with Tailwind CSS 4

- **Status**: Accepted
- **Date**: 2026-08-16
- **Supersedes**: None
- **Related specs**: 003-design-system, 004-ui-redesign

## Context

The ClashClanEvaluation frontend was functional but visually primitive. Tailwind CSS 4 was listed
in devDependencies but not configured — no `index.css`, no `@import "tailwindcss"`, no `@theme`
block. All utility classes rendered as nothing. The UI used emoji icons (🟡🔴⚫) and plain HTML
tables.

The rich visual interface plan (3 UX/UI expert perspectives) required:
- A dark theme with Clash Royale-inspired colors (deep navy, gold accent, card colors)
- 16 new components with consistent design tokens
- Animations, skeletons, toasts, modals

## Decision

Use **Tailwind CSS 4** with CSS-based configuration (`@theme` block in `index.css`) and the
`@tailwindcss/vite` plugin. No `tailwind.config.js` — Tailwind 4 uses CSS-first config.

Design tokens defined as CSS custom properties in `@theme`:
- Surface hierarchy: `--color-surface-0` through `--color-surface-4` (deep navy gradient)
- Primary: royal blue (`#2563eb`)
- Accent: trophy gold (`#f5a623`)
- Card system: yellow (`#facc15`), red (`#ef4444`), black (`#6366f1` — indigo, not literal black)
- Text: primary (`#f1f5f9`), secondary (`#94a3b8`), tertiary (`#64748b`)
- Fonts: Khand (display), Inter (body), JetBrains Mono (stats)
- Radius, shadows, animation easing curves

Arbitrary value classes used throughout: `bg-[var(--color-surface-2)]`,
`text-[var(--color-text-primary)]`, `rounded-[var(--radius-lg)]`, etc.

## Rationale

1. **Tailwind 4 CSS-first config** eliminates the need for a separate config file. The `@theme`
   block is co-located with base styles and animations in a single `index.css`.
2. **CSS custom properties** for design tokens enable runtime theming and are natively supported.
3. **Arbitrary value classes** (`bg-[var(--color-surface-2)]`) provide full access to tokens while
   keeping utility-class ergonomics.
4. **`@tailwindcss/vite` plugin** integrates with Vite's build pipeline — no PostCSS config needed.

## Alternatives considered

- **Tailwind 3 with `tailwind.config.js`**: Rejected — Tailwind 4 is already in devDependencies,
  and CSS-first config is simpler and more maintainable.
- **CSS Modules + styled-vars**: Rejected — loses utility-class ergonomics and requires more
  boilerplate per component.
- **shadcn/ui or Radix**: Rejected — adds dependency weight and opinionated structure. The
  primitives needed (Button, Card, Icon, Toast) are simple enough to build directly.

## Consequences

- **Positive**: Single source of truth for design tokens (`index.css` @theme). No config file.
  Full TypeScript safety on component props. Tree-shakeable utilities.
- **Negative**: Arbitrary value classes are verbose (`bg-[var(--color-surface-2)]` vs `bg-surface-2`).
  Could add semantic utility classes in `@layer components` to shorten, but current approach is
  explicit and readable.
- **Neutral**: `@tailwindcss/vite` must be in devDependencies and added to `plugins` in
  `vite.config.ts`.
