# Spec 005 — Landing Page

- **Status**: Draft · **Lane**: full · **Date**: 2026-08-17
- **Origin**: User — "o site deveria abrir uma landing page explicando o que ele faz"
- **Appetite**: 2 horas
- **Max user stories**: 5
- **UX design**: [[005-landing-page/ux-design.md]]

## What and why

O sistema abre diretamente no dashboard do clã, sem contexto. Um visitante novo não sabe o que o
sistema faz, não sabe que é focado em guerra (River Race), e não tem opção de ver apenas sua própria
performance sem ver todos os 92 membros.

A landing page serve como **ponto de entrada** que explica o propósito e oferece dois caminhos:
visão do clã (para líderes) e visão do jogador (para membros).

## User stories

### US1 — Hero section explicando o sistema
Como visitante, quero ver um hero com título "ClashClanEvaluation" e subtítulo explicando que o
sistema avalia participação de membros do clã em Guerras de Clãs (River Race) para que eu entenda
o propósito do site.

**Acceptance**: Hero com título, subtítulo, e fundo temático Clash Royale (dark navy + gold).

### US2 — Feature highlights
Como visitante, quero ver 3 cards explicando as funcionalidades principais (sistema de cartões,
recência/histórico, relaxamento de regras) para que eu entenda o valor do sistema.

**Acceptance**: 3 cards com ícone, título, e descrição curta. Ícones do sistema (card-yellow,$card-red, flag).

### US3 — Dois CTAs para entrar no sistema
Como visitante, quero dois botões: "Ver dados do Clã" (primário) e "Ver minha performance"
(secundário) para que eu escolha meu caminho.

**Acceptance**: Botão "Ver dados do Clã" navega para o dashboard. Botão "Ver minha performance"
navega para uma tela de input de tag do jogador.

### US4 — Tela de input de tag do jogador
Como jogador, quero inserir meu tag (#ABC123) e ver minha performance individual para que eu
acompanhe minha participação sem ver dados de outros.

**Acceptance**: Input com placeholder "#seu_tag", validação de formato, Enter ou botão "Ver" leva
para a página de detalhe do jogador.

### US5 — Navegação de volta à landing page
Como usuário em qualquer tela, quero poder voltar à landing page para que eu possa8mude de caminho
(clã → jogador ou vice-versa).

**Acceptance**: Logo no header é clicável e volta à landing page. Botão "Voltar" também disponível.

## Non-functional requirements

- **NFR1**: Landing page é a rota padrão (`/`), dashboard passa a ser `/clan`
- **NFR2**: Animação de entrada (fade-in staggered nos feature cards)
- **NFR3**: Responsivo — mobile mostra CTAs empilhados, desktop lado a lado
- **NFR4**: Footer de branding GHDaru visível (herda do Layout)

## Acceptance criteria

- [ ] Landing page abre em `/` com hero + features + CTAs
- [ ] "Ver dados do Clã" leva ao dashboard existente
- [ ] "Ver minha performance" leva a input de tag
- [ ] Tag válida leva à página do jogador
- [ ] Logo no header volta à landing page
- [ ] Responsivo em mobile

## Files

| File | Action |
|------|--------|
| `frontend/src/pages/Landing.tsx` | NEW — hero + features + CTAs |
| `frontend/src/pages/PlayerLookup.tsx` | NEW — input de tag |
| `frontend/src/App.tsx` | MODIFIED — add landing route, update navigation |
| `frontend/src/components/Layout.tsx` | MODIFIED — logo clickable to landing |

## Traceability

- UX design: [[005-landing-page/ux-design.md]]
- Spec anterior: [[004-ui-redesign/spec.md]]
- Branding: [[002-branding-ghdaru/spec.md]]
- Journey: [[docs/journey.md]] (new journey J5 — landing)
