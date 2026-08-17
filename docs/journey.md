# Journey — ClashClanEvaluation

> Living document of how a user experiences the system. Updated in the same PR as the code.

## Personas

- **Líder de Clã**: Decide sobre permanência, advertências e expulsões de membros com base em
  participação na River Race (Corrida do Rio).

## Journeys

### J1 — Avaliar participação do clã

```
Líder abre o painel
  → vê dashboard com status da guerra (progress bar 4 dias)
  → vê grid de jogadores com status (Limpo/Alerta/Perigo/Crítico), cartões (amarelo/vermelho/preto), trend
  → clica em "Avaliar" para coletar dados frescos da API
  → botão mostra spinner, toast de sucesso ao concluir
  → grid atualiza com dados mais recentes
```

**Served by**: Dashboard, PlayerCard, WarProgressBar, Toast, Button

### J2 — Analisar jogador individual

```
Líder clica em um PlayerCard
  → transição suave (View Transition) para PlayerDetail
  → vê header com avatar, nome, tag, role
  → vê guerra atual: ataques por dia, pontos, cartões, status
  → vê recência: trend (improving/stable/declining) + mini cards das últimas N semanas
  → vê histórico: lista expansível de guerras anteriores
  → clica "Voltar" para retornar ao dashboard
```

**Served by**: PlayerDetail, StatChip, TrendIndicator, Card, Button

### J3 — Configurar regras de avaliação

```
Líder clica em "Config"
  → vê seções em cards: parâmetros de ataque, thresholds de cartões, critérios de recência
  → ajusta valores em inputs estilizados
  → toggle switch para relax_on_first_place
  → clica "Salvar" → toast de sucesso
  → clica "Restaurar Defaults" → modal de confirmação → confirma → toast
```

**Served by**: ConfigPanel, ToggleSwitch, Modal, Toast, Button

### J4 — Identificar autoria

```
Qualquer usuário
  → vê footer "Desenvolvido por GHDaru Tecnologia"
  → clica no link → abre ghdaru.com.br em nova aba
  → vê copyright "ClashClanEvaluation © 2026"
```

**Served by**: Layout (footer)

## Error states

### E1 — Backend indisponível

```
  → query error
  → Error card com ícone, "Erro ao carregar dados", botão "Abrir Configuração"
```

### E2 — Erro de renderização

```
  → ErrorBoundary captura
  → tela mostra erro + stack trace + botão "Recarregar página"
```

### E3 — Sem guerra ativa

```
  → Dashboard mostra "Sem guerra ativa" no card de status
  → Se sem jogadores: empty state "Nenhum jogador encontrado" + CTA "Avaliar"
```
