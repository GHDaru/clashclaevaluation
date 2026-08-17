# Spec 002 — Branding GHDaru Tecnologia

- **Status**: Approved · **Lane**: full · **Date**: 2026-08-17
- **Origin**: Steward — identidade visual e rastreabilidade de autoria
- **Appetite**: 1 hora

## What and why

O sistema ClashClanEvaluation precisa exibir a autoria do desenvolvimento no rodapé de todas as
telas, com link para o site da empresa desenvolvedora. Isso garante rastreabilidade de autoria,
credibilidade e ponto de contato para suporte.

**Jornada servida**: qualquer usuário que visualize o painel identifica quem desenvolveu o sistema
e pode acessar o site da empresa.

## Functional requirements

### FR1 — Footer de autoria

- **FR1.1**: Todas as telas (Dashboard, PlayerDetail, ConfigPanel) exibem um rodapé no inferior
  da página com o texto "Desenvolvido por GHDaru Tecnologia".
- **FR1.2**: O texto "GHDaru Tecnologia" é um link clicável que abre `https://ghdaru.com.br` em
  uma nova aba (`target="_blank"`, `rel="noopener noreferrer"`).
- **FR1.3**: O rodapé exibe o ano atual dinamicamente: "ClashClanEvaluation © {ano}".
- **FR1.4**: O rodapé usa as cores de design tokens do sistema (accent gold para o link, text
  tertiary para o texto base).
- **FR1.5**: O rodapé é responsivo — em telas pequenas, os elementos se reorganizam com
  `flex-wrap`.

### FR2 — Posicionamento

- **FR2.1**: O rodapé fica fixo no inferior da viewport, após o conteúdo principal.
- **FR2.2**: O rodapé tem uma borda superior sutil (`border-t`) para separação visual.
- **FR2.3**: O rodapé não sobrepõe conteúdo — o layout usa `flex-col` com `min-h-screen` e o
  `main` tem `flex-1`.

## Non-functional requirements

- **NFR1**: O link usa `noopener noreferrer` para segurança (prevenção de tabnabbing).
- **NFR2**: O ano é calculado via `new Date().getFullYear()` — sem hardcode.
- **NFR3**: O rodapé herda o background do app (surface-0) — sem background próprio.

## Acceptance criteria

- [x] Footer visível em todas as 3 telas
- [x] Link "GHDaru Tecnologia" abre https://ghdaru.com.br em nova aba
- [x] Ano dinâmico no copyright
- [x] Cores seguem design tokens
- [x] Responsivo em mobile

## Implementation

- **Arquivo modificado**: `frontend/src/components/Layout.tsx`
- **Componente**: Footer adicionado dentro do `<div className="min-h-screen flex flex-col">`
- **Tokens usados**: `--color-accent`, `--color-accent-hover`, `--color-text-tertiary`,
  `--color-border`

## Traceability

- Spec anterior: [[001-clash-clan-eval/spec.md]]
- UX design: [[001-clash-clan-eval/ux-design.md]]
- ADR: [[docs/adr/0001-ddd-ubiquitous-language-hexagonal.md]]
