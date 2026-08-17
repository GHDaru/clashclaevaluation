# Data Model 001 — ClashClanEvaluation

- **Spec**: `spec.md` · **Plan**: `plan.md` · **Date**: 2026-08-16

---

## Entity-Relationship Diagram

```
Clan (1) ──────< (N) War ──────< (N) PlayerWar >───── (1) Player
                                          │
                                          │ (N:1)
                                          │
                                   EvaluationLog
```

---

## Entities

### Clan

| Field | Type | Constraints | Description |
|---|---|---|---|
| `tag` | `str(12)` | PK, format `#XXXXXXX` | Clan tag (immutable in CR) |
| `name` | `str(100)` | NOT NULL | Clan name |
| `created_at` | `datetime` | NOT NULL, DEFAULT NOW | First seen |
| `updated_at` | `datetime` | NOT NULL, ON UPDATE | Last updated |

### War

| Field | Type | Constraints | Description |
|---|---|---|---|
| `id` | `int` | PK, AUTOINCREMENT | Surrogate key |
| `clan_tag` | `str(12)` | FK → Clan.tag, NOT NULL | Clan |
| `start_date` | `date` | NOT NULL | Thursday of war week |
| `end_date` | `date` | NOT NULL | Sunday of war week |
| `status` | `str(10)` | `finished_1st`, `finished_2nd`, `finished_3rd`, `finished_4th`, `finished_5th` | Final position |
| `total_fame` | `int` | DEFAULT 0 | Clan total fame |
| `relaxed_days` | `json` | DEFAULT `[]` | Days where rules were relaxed (ex: `["sun"]`) |
| `created_at` | `datetime` | NOT NULL, DEFAULT NOW | When this war was recorded |

### Player

| Field | Type | Constraints | Description |
|---|---|---|---|
| `tag` | `str(12)` | PK, format `#XXXXXXX` | Player tag (immutable) |
| `clan_tag` | `str(12)` | FK → Clan.tag | Current clan (nullable: player may have left) |
| `name` | `str(100)` | NOT NULL | Player name (may change; upserted) |
| `role` | `str(20)` | `leader`, `coLeader`, `elder`, `member` | Clan role |
| `first_seen` | `datetime` | NOT NULL, DEFAULT NOW | First time seen |
| `last_seen` | `datetime` | NOT NULL | Most recent war participation |

### PlayerWar

| Field | Type | Constraints | Description |
|---|---|---|---|
| `id` | `int` | PK, AUTOINCREMENT | Surrogate key |
| `war_id` | `int` | FK → War.id, NOT NULL | War |
| `player_tag` | `str(12)` | FK → Player.tag, NOT NULL | Player |
| `attacks_day1` | `int` | DEFAULT 0, 0–4 | Attacks on Thursday |
| `attacks_day2` | `int` | DEFAULT 0, 0–4 | Attacks on Friday |
| `attacks_day3` | `int` | DEFAULT 0, 0–4 | Attacks on Saturday |
| `attacks_day4` | `int` | DEFAULT 0, 0–4 | Attacks on Sunday |
| `total_points` | `int` | DEFAULT 0 | Fame/points total |
| `yellow_cards` | `int` | DEFAULT 0 | Yellow cards this war |
| `red_cards` | `int` | DEFAULT 0 | Red cards this war |
| `black_cards` | `int` | DEFAULT 0 | Black cards this war |
| `incomplete` | `bool` | DEFAULT FALSE | TRUE if API data was partial |
| `created_at` | `datetime` | NOT NULL, DEFAULT NOW | When this record was created |

**Unique constraint**: `(war_id, player_tag)` — one record per player per war.

### EvaluationLog

| Field | Type | Constraints | Description |
|---|---|---|---|
| `id` | `int` | PK, AUTOINCREMENT | Surrogate key |
| `war_id` | `int` | FK → War.id, NOT NULL | War evaluated |
| `evaluated_at` | `datetime` | NOT NULL, DEFAULT NOW | When evaluation ran |
| `triggered_by` | `str(20)` | `manual`, `auto` | Who triggered |
| `config_snapshot` | `json` | NOT NULL | Config used for this evaluation (M4 params) |

---

## Indexes

| Index | Columns | Purpose |
|---|---|---|
| `idx_playerwar_war` | `war_id` | Fast lookup by war |
| `idx_playerwar_player` | `player_tag` | Fast lookup by player |
| `idx_playerwar_war_player` | `war_id, player_tag` | Unique constraint + join |
| `idx_war_clan_date` | `clan_tag, start_date` | War history by clan |
| `idx_evaluationlog_war` | `war_id` | Evaluation history |

---

## State transitions (PlayerWar lifecycle)

```
                    ┌──────────┐
                    │  (new)   │
                    └────┬─────┘
                         │ M1 collects data from API
                         ▼
                    ┌──────────┐
                    │ pending  │── incomplete=true (API error)
                    └────┬─────┘
                         │ M2 evaluates
                         ▼
                    ┌──────────┐
                    │ evaluated│── cards assigned
                    └──────────┘
```

---

## Migration notes

- Alembic gerencia schema. Primeira migration cria todas as 5 tabelas.
- SQLite: usar `render_as_batch=True` para operações ALTER.
- Constraints de FK: SQLite exige `PRAGMA foreign_keys = ON`.
- `config_snapshot` e `relaxed_days` como JSON: SQLite suporta nativamente via `JSON` type
  (armazenado como TEXT).
