# Spec 003 — Design System (Tokens + Primitives)

- **Status**: Retroactive · **Lane**: full · **Date**: 2026-08-16
- **Origin**: Rich Visual Interface plan (Expert 1 — Design Tokens)
- **Appetite**: 2 horas
- **Max user stories**: 5

## What and why

O frontend era funcional mas visualmente primitivo — Tailwind CSS 4 estava nas devDependencies
mas **não configurado**: sem `index.css`, sem `@import "tailwindcss"`, sem `@theme`. Todas as
classes `bg-gray-900` renderizavam como nada. O UI usava emojis (🟡🔴⚫) e tabelas HTML plain.

Esta spec estabelece o **design system** — tokens visuais e primitivos de UI — que serve de
base para todas as telas do ClashClanEvaluation.

## User stories

### US1 — Configurar Tailwind CSS 4
Como desenvolvedor, quero Tailwind 4 configurado com `@import "tailwindcss"` e plugin `@tailwindcss/vite`
para que as classes utilitárias gerem CSS real.

**Acceptance**: `pnpm dev` gera CSS com variáveis e utilitários. `body` tem `background-color: #0b1120`.

### US2 — Definir design tokens (cores, fontes, radius, shadows)
Como desenvolvedor, quero tokens de design no `@theme` block seguindo identidade Clash Royale
(tema dark navy, accent gold, card colors yellow/red/black) para que todos os componentes usem
valores consistentes.

**Acceptance**: `:root` contém `--color-surface-0` até `--color-surface-4`, `--color-accent`,
`--color-card-yellow/red/black`, `--color-text-primary/secondary/tertiary`, `--radius-*`, `--shadow-*`.

### US3 — Criar sistema de ícones SVG
Como desenvolvedor, quero um componente `Icon` tipado com 22 ícones SVG inline substituindo emojis
para que a UI tenha identidade visual profissional e acessível.

**Acceptance**: `Icon name="sword"` renderiza SVG. Todos os ícones têm `aria-hidden="true"`.

### US4 — Criar primitivos de UI (Button, Card, StatChip, Badge)
Como desenvolvedor, quero componentes base reutilizáveis (Button com 4 variantes, Card com hover,
StatChip com tabular-nums, StatusBadge, CardBadge, TrendIndicator) para que as páginas composem UI
consistente.

**Acceptance**: Button tem variantes primary/secondary/ghost/danger, focus-visible ring, touch-manipulation.
Card tem shadow, border, radius. StatChip tem tabular-nums.

### US5 — Criar componentes de feedback (Toast, Modal, Skeleton, Toggle)
Como desenvolvedor, quero Toast (auto-dismiss, aria-live), Modal (backdrop blur, ESC), Skeleton
(shimmer), ToggleSwitch (role="switch") para que a UX tenha feedback adequado.

**Acceptance**: ToastProvider + useToast hook. Modal fecha com ESC e click outside. Skeleton anima
com shimmer. ToggleSwitch tem aria-checked.

## Non-functional requirements

- **NFR1**: `color-scheme: dark` no `:root` (scrollbars e inputs nativos dark)
- **NFR2**: `prefers-reduced-motion: reduce` desativa todas as animações
- **NFR3**: `touch-action: manipulation` em buttons (elimina 300ms tap delay)
- **NFR4**: `focus-visible:ring-2` em todos os elementos interativos
- **NFR5**: Animações só animam `transform` e `opacity` (Vercel guideline)

## Files

| File | Action |
|------|--------|
| `frontend/src/index.css` | NEW — Tailwind 4 entry + @theme + base + animations |
| `frontend/src/main.tsx` | MODIFIED — add `import "./index.css"` |
| `frontend/index.html` | MODIFIED — meta theme-color, fonts, dark class |
| `frontend/vite.config.ts` | MODIFIED — add tailwindcss() plugin |
| `frontend/src/components/Icon.tsx` | NEW |
| `frontend/src/components/Button.tsx` | NEW |
| `frontend/src/components/Card.tsx` | NEW |
| `frontend/src/components/StatChip.tsx` | NEW |
| `frontend/src/components/CardBadge.tsx` | NEW |
| `frontend/src/components/StatusBadge.tsx` | NEW |
| `frontend/src/components/TrendIndicator.tsx` | NEW |
| `frontend/src/components/WarProgressBar.tsx` | NEW |
| `frontend/src/components/Skeleton.tsx` | NEW |
| `frontend/src/components/Toast.tsx` | NEW |
| `frontend/src/components/Modal.tsx` | NEW |
| `frontend/src/components/ToggleSwitch.tsx` | NEW |
| `frontend/src/components/Logo.tsx` | NEW |

## Traceability

- Plan: [[floating-crafting-haven]] (Expert 1 — Design Tokens, Expert 2 — Interface Objects)
- Spec anterior: [[001-clash-clan-eval/spec.md]]
- ADR: [[docs/adr/0002-design-system-tailwind4.md]]
