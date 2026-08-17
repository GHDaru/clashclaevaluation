# Spec 004 — UI Redesign (Layout + Pages)

- **Status**: Retroactive · **Lane**: full · **Date**: 2026-08-16
- **Origin**: Rich Visual Interface plan (Expert 2 — Interface Objects, Expert 3 — Directives)
- **Appetite**: 3 horas
- **Max user stories**: 5
- **Depends on**: [[003-design-system/spec.md]]

## What and why

Com o design system estabelecido (Spec 003), as páginas precisam ser redesenhadas para usar os
novos primitivos. O layout atual usa tabela HTML, emojis, e zero animação. O redesenho cria uma
experiência rica com card grid, war progress bar, skeleton loading, page transitions, e feedback
via toast.

## User stories

### US1 — Layout shell com header sticky e footer
Como usuário, quero um header sticky com logo + título + ações (Avaliar, Config) e footer com
branding GHDaru para que a navegação seja sempre acessível e a autoria visível.

**Acceptance**: Header sticky com backdrop-blur. Footer "Desenvolvido por GHDaru Tecnologia" link
para ghdaru.com.br. Layout usa min-h-screen flex flex-col.

### US2 — Dashboard com card grid e war progress
Como líder de clã, quero ver o status da guerra (progress bar 4 dias) e jogadores em card grid
responsivo (1/2/3 colunas) com status, cartões, trend, e stats para que eu avalie participação
rapidamente.

**Acceptance**: WarProgressBar mostra 4 dias (Qui/Sex/Sáb/Dom). PlayerCard grid responsivo.
Empty state com CTA "Avaliar". Skeleton loading durante fetch.

### US3 — PlayerDetail redesenhado
Como líder, quero ver detalhes do jogador em cards (header com avatar, guerra atual com stats,
recência com trend, histórico expansível) para que eu tome decisões informadas sobre permanência.

**Acceptance**: Player header Card. Current war Card com 4 StatChips. Recency Card com
TrendIndicator. History Card com expand/collapse. Skeleton loading.

### US4 — ConfigPanel redesenhado
Como líder, quero configurar regras em cards com inputs estilizados, toggle switch, e confirmação
modal para restaurar defaults para que a configuração seja clara e segura.

**Acceptance**: SectionCard com ícone + título. Inputs dark com focus ring. ToggleSwitch para
boolean. Modal de confirmação para restore. Toast em save/error.

### US5 — Page transitions e animações
Como usuário, quero transições suaves entre páginas (View Transitions API) e animações staggered
nos cards para que a UI seja fluida e profissional.

**Acceptance**: `document.startViewTransition` em navegação. Cards com animate-fade-in
staggered 50ms. `prefers-reduced-motion` desativa animações.

## Non-functional requirements

- **NFR1**: Error Boundary captura erros de renderização (não tela em branco)
- **NFR2**: `aria-live="polite"` no container de toast
- **NFR3**: Keyboard accessible — Enter/Space em PlayerCard navega para detalhe
- **NFR4**: Responsive — 375px width sem scroll horizontal

## Files

| File | Action |
|------|--------|
| `frontend/src/components/Layout.tsx` | NEW — header + main + footer |
| `frontend/src/components/PlayerCard.tsx` | NEW — replaces PlayerRow |
| `frontend/src/components/ErrorBoundary.tsx` | NEW — catch render errors |
| `frontend/src/App.tsx` | MODIFIED — ToastProvider, Layout, View Transitions |
| `frontend/src/pages/Dashboard.tsx` | MODIFIED — card grid, war progress, skeletons |
| `frontend/src/pages/PlayerDetail.tsx` | MODIFIED — card layout, stat chips, timeline |
| `frontend/src/pages/ConfigPanel.tsx` | MODIFIED — card sections, styled inputs, modal |
| `frontend/src/components/PlayerRow.tsx` | DELETED |

## Traceability

- Plan: [[floating-crafting-haven]] (Expert 2 — Interface Objects, Expert 3 — Directives)
- Spec anterior: [[003-design-system/spec.md]]
- Branding: [[002-branding-ghdaru/spec.md]]
- ADR: [[docs/adr/0002-design-system-tailwind4.md]]
