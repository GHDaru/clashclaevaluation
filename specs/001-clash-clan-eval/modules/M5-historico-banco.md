# M5 — Histórico e Banco de Dados (Nível 1: Persistência)

- **Spec pai**: `specs/001-clash-clan-eval/spec.md` · **Lane**: full · **Date**: 2026-08-16
- **Épico**: Persistência — a memória do sistema entre guerras

## What and why

Sem persistência, cada avaliação é um evento isolado. Com o banco, o sistema acumula um
histórico que permite análise de tendências, comparação entre guerras e a visão expansível de
3 meses que o painel (M3) exibe. A persistência também evita chamadas repetidas à API para
battlelogs já coletados (cache de longo prazo).

---

## Modelo de dados

```
┌──────────────┐       ┌──────────────────┐       ┌─────────────────┐
│    Clan      │       │       War        │       │   PlayerWar     │
├──────────────┤       ├──────────────────┤       ├─────────────────┤
│ tag (PK)     │──1:N──│ id (PK)          │──1:N──│ id (PK)         │
│ name         │       │ clan_tag (FK)    │       │ war_id (FK)     │
│ created_at   │       │ start_date       │       │ player_tag (FK) │
│ updated_at   │       │ end_date         │       │ player_name     │
└──────────────┘       │ status (1st/2nd) │       │ attacks_day1    │
                       │ total_fame       │       │ attacks_day2    │
                       │ created_at       │       │ attacks_day3    │
                       └──────────────────┘       │ attacks_day4    │
                                                  │ total_points    │
               ┌──────────────────┐               │ yellow_cards    │
               │     Player       │               │ red_cards       │
               ├──────────────────┤               │ black_cards     │
               │ tag (PK)         │──1:N──────────│ relaxed_days    │
               │ clan_tag (FK)    │               │ created_at      │
               │ name             │               └─────────────────┘
               │ role             │
               │ first_seen       │       ┌──────────────────┐
               │ last_seen        │       │   EvaluationLog  │
               └──────────────────┘       ├──────────────────┤
                                          │ id (PK)          │
                                          │ war_id (FK)      │
                                          │ evaluated_at     │
                                          │ triggered_by     │
                                          │ config_snapshot  │
                                          └──────────────────┘
```

---

## Functional requirements

### F5.1 — Armazenamento de dados de guerra

- **FR5.1.1**: Ao final de cada avaliação pós-guerra, o sistema persiste:
  - Dados da guerra (`War`): datas, status final, pontuação total do clã
  - Dados por jogador (`PlayerWar`): ataques por dia, pontos, cartões recebidos
  - Snapshot da configuração usada (`EvaluationLog.config_snapshot`)
- **FR5.1.2**: Jogadores novos são registrados na tabela `Player` (upsert: se a tag já
  existe, atualiza nome e last_seen).
- **FR5.1.3**: O battlelog cacheado evita re-chamadas à API: se o `PlayerWar` já tem dados
  para aquela guerra, o M1 pode pular a consulta.

### F5.2 — API de consulta histórica

- **FR5.2.1**: Consulta por jogador: `GET /api/players/{tag}/history` retorna:
  - Últimas N guerras (default: 4 = recência)
  - Cada guerra com: datas, ataques/dia, pontos, cartões
  - Agregações: total de cartões no período, tendência
- **FR5.2.2**: Consulta por guerra: `GET /api/wars/{id}` retorna o status de todos os
  jogadores naquela guerra.
- **FR5.2.3**: Parâmetro `?expand=true` estende a consulta para 3 meses (12 guerras).

---

## Stack sugerida (para o plano técnico)

- **Backend**: Python (FastAPI) gerenciado por `uv`
- **ORM**: SQLAlchemy + Alembic (migrations)
- **Banco**: SQLite (v1 single-user) ou PostgreSQL (se multi-usuário)
- **Frontend**: React + pnpm (consome a API do backend)

---

## Edge cases

- **Primeira execução (banco vazio)**: cria schema via migration automática.
- **Jogador muda de nome**: upsert por tag (tag é imutável no Clash Royale, nome não).
- **Guerra sem dados completos** (API falhou no meio): `PlayerWar` com campos parciais,
  marcado `incomplete = true`.
- **Migration de schema**: Alembic gerencia versões. Rollback suportado.

---

## Dependências

| Entrada | De onde vem | O que fornece |
|---|---|---|
| Dados da guerra | M1 (API) | Clan, War, Players |
| Cartões calculados | M2 (Motor) | PlayerWar (cards) |
| Configuração | M4 (Config) | Snapshot para EvaluationLog |

| Saída | Para onde vai | O que entrega |
|---|---|---|
| Histórico | M3 (Painel) | Dados para T2 (detalhe do jogador) |
| Cache | M1 (API) | Evita re-chamadas à API para dados já coletados |
