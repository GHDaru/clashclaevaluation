# M4 — Gerenciamento de Regras (Nível 1: Configuração)

- **Spec pai**: `specs/001-clash-clan-eval/spec.md` · **Lane**: full · **Date**: 2026-08-16
- **Épico**: Configuração — os parâmetros que governam o Motor de Avaliação

## What and why

Todas as regras do M2 são configuráveis. Este módulo expõe os parâmetros e os persiste, para
que o líder ajuste a rigidez da avaliação ao perfil do clã — um clã competitivo pode ser mais
rígido; um clã casual pode ser mais flexível.

---

## Parâmetros configuráveis

### Grupo A — Cartões (thresholds de conversão)

| Parâmetro | Default | Range | Descrição |
|---|---|---|---|
| `yellow_to_red` | 4 | 2–10 | Quantos 🟡 amarelos viram 1 🔴 vermelho |
| `red_to_black` | 4 | 2–10 | Quantos 🔴 vermelhos viram 1 ⚫ preto |

### Grupo B — Pontuação

| Parâmetro | Default | Range | Descrição |
|---|---|---|---|
| `min_points_warning` | 1600 | 0–10000 | Abaixo = +1 🟡 amarelo |
| `min_points_critical` | 0 (desligado) | 0–10000 | Abaixo = +1 🔴 vermelho (0 = desligado) |

### Grupo C — Guerra

| Parâmetro | Default | Range | Descrição |
|---|---|---|---|
| `attacks_per_day` | 4 | 1–4 | Ataques esperados por dia |
| `war_days` | ["qui","sex","sáb","dom"] | subconjunto | Dias de batalha na guerra |

### Grupo D — Recência e histórico

| Parâmetro | Default | Range | Descrição |
|---|---|---|---|
| `recency_weeks` | 4 | 1–12 | Semanas com peso ativo (corrida dos campeões) |
| `history_months` | 3 | 1–12 | Meses de histórico expansível |

### Grupo E — Relaxamento

| Parâmetro | Default | Range | Descrição |
|---|---|---|---|
| `relax_on_first_place` | true | bool | Suspende cartões após vitória antecipada |

---

## Functional requirements

### F4.1 — Tela de parâmetros

- **FR4.1.1**: O sistema exibe todos os parâmetros agrupados (A–E) com valor atual, default e
  descrição.
- **FR4.1.2**: O usuário pode alterar qualquer parâmetro. Valores fora do range são
  rejeitados com mensagem.
- **FR4.1.3**: Um botão "Restaurar defaults" retorna todos os parâmetros ao valor padrão.
- **FR4.1.4**: Alterações têm efeito **na próxima avaliação** (não alteram cartões já
  emitidos).

### F4.2 — Persistência de configuração

- **FR4.2.1**: Os parâmetros são persistidos como JSON (arquivo de configuração ou banco).
- **FR4.2.2**: O sistema carrega a configuração ao iniciar. Se ausente, cria com defaults.
- **FR4.2.3**: Migração de schema: se uma versão futura adicionar novos parâmetros, valores
  ausentes são preenchidos com defaults (nunca quebra).

---

## Estrutura de configuração (exemplo)

```json
{
  "version": 1,
  "cards": {
    "yellow_to_red": 4,
    "red_to_black": 4
  },
  "scoring": {
    "min_points_warning": 1600,
    "min_points_critical": 0
  },
  "war": {
    "attacks_per_day": 4,
    "war_days": ["thu", "fri", "sat", "sun"]
  },
  "recency": {
    "recency_weeks": 4,
    "history_months": 3
  },
  "relaxation": {
    "relax_on_first_place": true
  }
}
```

---

## Edge cases

- **Configuração corrompida**: arquivo JSON inválido → carrega defaults e alerta o usuário.
- **Valores extremos**: `yellow_to_red = 1` significaria cada amarelo vira vermelho
  imediatamente. O range (2–10) evita isso.
- **`min_points_critical = 0`**: significa "desligado" — a faixa crítica não é aplicada.
- **`war_days` vazio**: sem dias de guerra definidos → sistema alerta e não avalia.

---

## Dependências

| Entrada | De onde vem | O que fornece |
|---|---|---|
| Nada (standalone) | — | M4 é fonte de configuração para M2 e M1 |

| Saída | Para onde vai | O que entrega |
|---|---|---|
| Parâmetros | M2 (Motor) | Thresholds, mínimos, flags |
| Clan tag + API key | M1 (API) | Identificação e autenticação |
