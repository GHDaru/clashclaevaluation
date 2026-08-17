# Plan 008 — Coleta Diária de Snapshots de Guerra

- **Spec**: `spec.md` · **Lane**: full · **Date**: 2026-08-17

## Technical Context

- **Backend**: Python 3.12, FastAPI, SQLAlchemy 2.0 async, asyncpg, PostgreSQL on Neon, Alembic.
- **Frontend**: React 19, TypeScript, Vite 7, TanStack React Query, Tailwind 4.
- **Architecture**: Hexagonal / Ports & Adapters (ADR 001). Domain pure, application orchestrates,
  infrastructure adapts. Dependency unidirectional toward the domain.
- **Key existing assets** (most of the persistence + domain layer is already in place):
  - Migration `a1b2c3d4e5f6` → `war_snapshots`; migration `b2c3d4e5f6a7` → `snapshot_runs`
    (chains correctly: `dfcf5ad77d2e` → `a1b2c3d4e5f6` → `b2c3d4e5f6a7`).
  - ORM: `WarSnapshotModel`, `SnapshotRunModel` (`backend/infrastructure/orm/models.py`).
  - Domain: `WarSnapshot`, `SnapshotRun`, `derive_per_day_attacks()`
    (`backend/domain/model/aggregates.py`) — **already implemented**.
  - Ports: `WarSnapshotRepository`, `SnapshotRunRepository`
    (`backend/application/port/secondary/repositories.py`).
  - SQL adapters: `SqlWarSnapshotRepository`, `SqlSnapshotRunRepository`
    (`backend/infrastructure/adapter/secondary/sql_repositories.py`).
  - CR API port `CRApiClient.get_current_war` → `CurrentWarData` (with `WarParticipant`:
    `tag, name, fame, decks_used, decks_used_today`); HTTP impl already retries 429.
  - DI: `backend/application/di.py`. Routes: `backend/infrastructure/adapter/primary/fastapi_routes.py`.
  - Use cases: `backend/application/port/primary/use_cases.py` (`EvaluateClanUseCase`).

## Constitution Check (governance/principles.md)

| Principle | Compliance |
|---|---|
| I. Spec-driven | ✅ Plan derives from the approved spec at `specs/008-daily-war-snapshots/spec.md`; every task traces to an FR. |
| II. Human-governed orchestration | ✅ Human is Accountable for the gate; agents implement behind decision gates. Cron scheduling is explicitly ops-owned (human), not delegated to the app. |
| III. Reversibility / risk gates | ✅ Snapshots are additive (upsert, unique constraint); no destructive writes. Backfill is idempotent. Worst case = extra rows, trivially deletable. Migration already exists and is reversible (`downgrade`). |
| IV. Test-first / verifiable DoD | ✅ DoD commands below are autonomously verifiable (idempotency double-run, grep for `derive_per_day_attacks`, endpoint + unit tests). Tests accompany each boundary. |
| V. Context economy / boundary | ✅ Work is cut along bounded contexts (Collection / Evaluation-integration / Frontend / Tests) enabling parallel work; data-model.md + contracts/ carry the integrating context. |
| VI. Living artifacts | ✅ Plan, data-model, contracts and ADR live with the code in the same PR; no external doc duplication (existing docstrings are referenced, not copied). |
| VII. Light governance / YAGNI | ✅ No internal scheduler imported (cron suffices, ADR 004). Frontend terminology fix is already in place — reduced to verification, no redundant work. No new migration (schema already exists). |
| VIII. Intelligible communication | ✅ Acronyms expanded on first occurrence: Domain-Driven Design (DDD), Application Dependency Injection (DI), Data Transfer Object (DTO), Definition of Done (DoD), FastAPI background task (BackgroundTasks). |

**No violations. Complexity Tracking: none.**

## Artifacts of this cycle (declare all five — silence is not a decision)

| Artifact | Declaration | Why |
|---|---|---|
| `research.md` | `ART:research=no` | No technical unknown remains: the CR API exposes only cumulative counters (already confirmed and documented in the spec), and the diff strategy is proven by the existing `derive_per_day_attacks`. |
| `data-model.md` | `ART:data-model=yes` | Code feature with entities/relations (WarSnapshot, SnapshotRun, idempotency constraint, derive function) and new use-case DTOs. File created; records what already exists vs. what is new so the implementer does not recreate existing layers. |
| `contracts/` | `ART:contracts=yes` | New interfaces between parts: `CollectSnapshotsUseCase` port, CLI adapter, two HTTP endpoints, and the `EvaluateClanUseCase` integration seam. File created at `contracts/snapshot-contracts.md`. |
| `checklist.md` | `ART:checklist=no` | A requirements checklist already exists at `specs/008-daily-war-snapshots/checklists/requirements.md`; duplicating it would violate Principle VI. |
| `ux-design.md` | `ART:ux-design=no` | No screen design decision: the only UI change is a label terminology fix ("fama total"→"troféus", "fama hoje"→"pontos hoje") which is a text correction, not a UX design. Verification confirms the labels are already correct in `frontend/src/pages/Dashboard.tsx` (lines 67, 72) and no "fama" string exists anywhere in the frontend. |

## How

### Architectural decision (ADR 004 — immutable)

Collection runs as a **standalone script** (`scripts/snapshot_war.py`) scheduled by external
cron (`30 5 * * 4-7`, 05:30 UTC Thu–Sun), not a FastAPI background task. The same
`CollectSnapshotsUseCase` is shared by the CLI and the manual HTTP endpoint, so there is one
testable orchestration path. Scheduling is ops-owned. See
`docs/adr/0004-standalone-cron-snapshot-collection.md`.

### Cutting by boundary (bounded context — parallel-safe)

Four boundaries. Dependencies are one-way; parallel work is safe where noted.

#### Boundary A — Collection use case (application)
- New `CollectSnapshotsUseCase` + DTOs (`CollectSnapshotsCommand`, `CollectSnapshotsResultDTO`).
- Orchestration: resolve `war_id` (`WarRepository.get_by_clan_and_date`; create minimal `War`
  stub if absent so snapshots have an FK anchor) → `CRApiClient.get_current_war` →
  `state ∉ {active, warDay, full}` ⇒ log `SnapshotRun(no_war)` and return → else upsert one
  `WarSnapshot` per participant (`WarSnapshotRepository.save`) → log
  `SnapshotRun(success, participants_captured=N)`. On unrecoverable API error ⇒
  `SnapshotRun(failure, error_message=...)`; a failure run must not coexist with a success run
  for the same execution (DoD).
- Idempotency relies on the existing unique constraint `uq_warsnapshot_war_player_date`.
- **No dependency on other boundaries.** This is the core; B and C depend on it (B) or are
  independent (C).

#### Boundary B — Primary adapters + DI (infrastructure)
- **CLI** `scripts/snapshot_war.py`: argparse (`--date`, `--clan-tag`), builds async DI
  (reuses `application.di` factories), calls `CollectSnapshotsUseCase`, retry loop (≤3
  attempts, exponential backoff) only on `status="failure"`; `no_war` is terminal. Exit code
  0 on success/no_war, non-zero on failure.
- **HTTP** in `fastapi_routes.py`: `POST /api/v1/snapshots/collect` (body `snapshot_date?`,
  `triggered_by="manual"`) and `GET /api/v1/snapshots/missing` (computes 4 expected war days
  from current war start, returns missing via `SnapshotRunRepository.get_missing_dates`).
- **DI** (`di.py`): add `get_war_snapshot_repo()`, `get_snapshot_run_repo()`,
  `get_collect_snapshots_use_case()`; register route wiring.
- **Depends on A.** Not parallel with A; parallel with C and D.

#### Boundary C — Evaluation integration (application)
- Modify `EvaluateClanUseCase`: inject `WarSnapshotRepository`. After resolving `war_id`,
  if `get_by_war(war_id)` returns snapshots, group by player and build `attacks` via
  `derive_per_day_attacks(player_snapshots, war_start_date)`; else current heuristic (FR7).
- No change to `EvaluationService` or domain contracts — only the `attacks` source changes.
- **Independent of A and B** (touches a different use case; depends only on the already-existing
  `WarSnapshotRepository` + `derive_per_day_attacks`). **Parallel-safe with B and D.**

#### Boundary D — Frontend terminology fix (frontend)
- Verification-only: `frontend/src/pages/Dashboard.tsx` already uses `"Troféus"` (line 67) and
  `"Pontos Hoje"` (line 72); grep confirms no `"fama total"` / `"fama hoje"` anywhere in the
  frontend. Task = assert this remains true (a regression guard test/check), no code change
  expected. If a stray label is found elsewhere, fix it to the canonical terms.
- **Independent of A, B, C. Parallel-safe.**

#### Boundary E — Tests (accompany each boundary, test-first)
- `backend/tests/application/test_collect_snapshots.py` — use case with a fake
  `CRApiClient` (active war, no_war, API failure), fake repos; asserts upsert count, run
  status, idempotency on double-run, failure/success exclusivity.
- `backend/tests/api/test_snapshot_routes.py` — `POST /collect` + `GET /missing` via
  FastAPI TestClient with overridden DI.
- `backend/tests/application/test_evaluate_with_snapshots.py` — `EvaluateClanUseCase` uses
  real per-day attacks when snapshots present; falls back when absent.
- `backend/tests/domain/test_derive_per_day_attacks.py` — pure domain tests for the derive
  function (missing day, join-mid-war, today-count preferred over diff, cap at 4).
- CLI idempotency covered by the DoD double-run command.

### Phase 0 — research
None (ART:research=no).

### Phase 1 — data-model + contracts
`data-model.md` and `contracts/snapshot-contracts.md` created in this cycle (see Artifacts
table). They record the existing layers (so they are not recreated) and define the new
use-case/adapter contracts.

## Verification (DoD)

- `python -m pytest backend/tests/application/test_collect_snapshots.py backend/tests/api/test_snapshot_routes.py backend/tests/application/test_evaluate_with_snapshots.py backend/tests/domain/test_derive_per_day_attacks.py` → all green.
- `python scripts/snapshot_war.py --date 2026-08-14 --clan-tag "#QPUJC0CG"` executed twice →
  `war_snapshots` contains exactly one row per participant for `(war_id, *, 2026-08-14)`
  (idempotency; FR2/DoD).
- `grep -r "derive_per_day_attacks" backend/` → non-empty (function exists and is called;
  DoD).
- `grep -ri "fama total\|fama hoje" frontend/` → empty (terminology fix holds; Boundary D).
- `curl -X POST /api/v1/snapshots/collect` and `curl /api/v1/snapshots/missing` → 200 with
  the contract shapes in `contracts/snapshot-contracts.md`.
- `alembic upgrade head` → succeeds (migrations `a1b2c3d4e5f6`, `b2c3d4e5f6a7` already
  present; no new migration expected).

<!--
  GATE (not delegable): the plan is approved by a human before it becomes tasks.
  Handoff: plan-architect → (approval) → tasks → dev-implementer.
-->
