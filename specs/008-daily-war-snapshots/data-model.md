# Data Model — Spec 008 (Daily War Snapshots)

- **Spec**: `spec.md` · **Date**: 2026-08-17

> Snapshot of the domain model touched by this feature. Most of the persistence and domain
> layer **already exists** (migrations, ORM models, aggregates, repository ports and SQL
> adapters). This document records what exists and what this cycle adds, so the implementer
> has the integrating context in one place (Principle V/VI).

## Existing — already implemented (do NOT recreate)

### Domain aggregates (`backend/domain/model/aggregates.py`)

- **`WarSnapshot`** — point-in-time capture of a player's cumulative war progress.
  Fields: `war_id`, `player_tag: PlayerTag`, `player_name`, `snapshot_date: date`,
  `decks_used_at_snapshot` (cumulative 0–16), `decks_used_today_at_snapshot` (0–4),
  `fame_at_snapshot` (cumulative), `captured_at`.
  Methods: `attacks_since(prior)` = diff of cumulative decks; `fame_since(prior)` = diff of
  cumulative fame. `prior=None` ⇒ full cumulative (handles join-mid-war).
  Part of the `War` aggregate (War is the root).

- **`SnapshotRun`** — audit record of one collection execution.
  Fields: `war_id | None`, `clan_tag`, `snapshot_date`, `status ∈ {success, failure, no_war}`,
  `participants_captured`, `error_message`, `triggered_by ∈ {cron, manual}`, `captured_at`.

- **`derive_per_day_attacks(snapshots, war_start_date) -> list[AttackCount]`** — derives
  exactly 4 per-day attack counts. Prefers `decks_used_today_at_snapshot` (API's own per-day
  count); falls back to cumulative diff when today-count is 0 but diff is positive; missing
  days ⇒ 0; caps at 4. **Already implemented and the spec acceptance grep target.**

### Persistence

- Migration `a1b2c3d4e5f6` → table `war_snapshots` (FK `wars.id`, `players.tag`; unique
  `uq_warsnapshot_war_player_date` on `(war_id, player_tag, snapshot_date)`; index
  `ix_warsnapshot_war_date` on `(war_id, snapshot_date)`).
- Migration `b2c3d4e5f6a7` (rev `a1b2c3d4e5f6`) → table `snapshot_runs` (FK `wars.id`;
  index `ix_snapshot_runs_date`).
- ORM: `WarSnapshotModel`, `SnapshotRunModel` (`backend/infrastructure/orm/models.py`).

### Repository ports (`backend/application/port/secondary/repositories.py`)

- `WarSnapshotRepository`: `get_by_war`, `get_by_war_and_player`, `save` (upsert).
- `SnapshotRunRepository`: `save`, `get_by_war`, `get_missing_dates(war_id, expected_dates)`.

### SQL adapters (`backend/infrastructure/adapter/secondary/sql_repositories.py`)

- `SqlWarSnapshotRepository`, `SqlSnapshotRunRepository` — already implemented.

## New this cycle

### Application layer

- **`CollectSnapshotsUseCase`** (new, `backend/application/port/primary/use_cases.py` or a new
  `snapshot_use_cases.py`) — orchestrates: resolve `war_id` (find `War` by clan+war-start-date
  via `WarRepository`; create minimal `War` stub if absent) → fetch `CurrentWarData` via
  `CRApiClient.get_current_war` → if state not active/warDay, log `SnapshotRun(no_war)` → else
  upsert one `WarSnapshot` per participant via `WarSnapshotRepository.save` → log
  `SnapshotRun(success, participants_captured=N)`. On unrecoverable API failure, log
  `SnapshotRun(failure, error_message=...)`.
  - DTOs: `CollectSnapshotsCommand(clan_tag, snapshot_date=None, triggered_by="cron")`,
    `CollectSnapshotsResultDTO(war_id, snapshot_date, status, participants_captured, error)`.

- **`EvaluateClanUseCase` integration** (modify existing) — inject `WarSnapshotRepository`;
  after resolving the current `war_id`, if snapshots exist for that war, build per-day attacks
  via `derive_per_day_attacks` per player instead of the current even-distribution heuristic.
  Fallback to the existing heuristic when no snapshots exist (FR7).

### No schema changes

All tables, constraints, indexes and ORM models already exist. No new migration is needed.
