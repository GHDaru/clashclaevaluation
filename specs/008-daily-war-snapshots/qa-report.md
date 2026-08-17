# QA Report — Spec 008 — Coleta Diária de Snapshots de Guerra

- **Date**: 2026-08-17
- **Verifier**: QA agent (read-only verification)
- **Spec**: `specs/008-daily-war-snapshots/spec.md`
- **Plan**: `specs/008-daily-war-snapshots/plan.md`

## Verification method

Read the implementation files (`use_cases.py`, `sql_repositories.py`, `fastapi_routes.py`,
`snapshot_war.py`, `di.py`, `models.py`, `aggregates.py`), checked each acceptance criterion
against the code, ran Python import checks, ran an in-memory SQLAlchemy test to verify the
upsert/idempotency mechanism, ran `derive_per_day_attacks` inline, ran `npx tsc --noEmit` in
the frontend, and checked the frontend terminology.

## Acceptance criteria

| # | Criterion | Verdict | Evidence |
|---|---|---|---|
| 1 | Active war → snapshot per participant with decksUsed and fame | **PASS** | `CollectSnapshotUseCase.execute` (use_cases.py:580-592) loops `war_data.participants` and builds a `WarSnapshot` per participant with `decks_used_at_snapshot=p.decks_used` and `fame_at_snapshot=p.fame`. |
| 2 | Double-run same war/player/date → exactly one record (upsert) | **FAIL** | `SqlWarSnapshotRepository.save` (sql_repositories.py:296-311) calls `session.merge(model)` with an **unset PK** (`id` autoincrement, never loaded). SQLAlchemy `merge` with `id=None` performs an **INSERT**, not an upsert. Verified with an in-memory SQLite+aiosqlite test: the second `merge` raises `IntegrityError` on the unique constraint `uq_warsnapshot_war_player_date`. The code comment ("merge = upsert on the unique constraint when the PK id is unset") is incorrect. The second run crashes instead of updating. |
| 3 | API returns "ended"/"notInWar" → run status "no_war", no player snapshots | **PARTIAL FAIL** | use_cases.py:540: `war_data.state not in ("active", "full", "warDay", "ended")`. The state `"ended"` is **included** in the active set, so the code proceeds to capture snapshots and logs `success` — directly contradicting AC3 which requires `"ended" → no_war`. `"notInWar"` correctly falls through to `no_war`. Half of AC3 passes. |
| 4 | API unavailable, retries fail → run "failure", no "success" | **PASS** | use_cases.py:525-538 wraps `get_current_war` in try/except, logs a `SnapshotRun(status="failure")` and returns `SnapshotResultDTO(status="failure")` without creating any snapshot or success run. |
| 5 | Snapshots days 1,2,3 → attacks_dia_2 = decksUsed_dia2 − decksUsed_dia1 | **PASS** (with caveat) | `derive_per_day_attacks` (aggregates.py:163-217) computes `diff = snap.attacks_since(prior)` = `decks_used_at_snapshot − prior.decks_used_at_snapshot`. Verified inline with cumulative decks [4,8,12] and `decks_used_today=0`: day2 = 4 = 8−4. **Caveat**: the implementation prefers `decks_used_today_at_snapshot` over the diff when `today > 0` (aggregates.py:211). This is a documented design decision (plan Boundary E: "today-count preferred over diff") but deviates from the literal spec formula. The diff formula is only the fallback path. |
| 6 | Completeness check, 4 expected days, 2 snapshots → 2 missing dates | **PASS** | `CheckCompletenessUseCase.execute` (use_cases.py:641-666) builds 4 expected dates (Thu–Sun) and calls `SnapshotRunRepository.get_missing_dates`, which (sql_repositories.py:353-364) returns expected dates with no `status="success"` run. With 2 successful runs, exactly 2 missing dates are returned. |
| 7 | Evaluation with complete snapshots → real per-day attacks, not heuristic | **PASS** | `EvaluateClanUseCase.execute` (use_cases.py:298-318) loads snapshots via `snapshot_repo.get_by_war`, groups by player, and calls `derive_per_day_attacks(player_snaps, start_date)` when `player_snaps` is non-empty. `di.py:108` injects `snapshot_repo=get_war_snapshot_repo()` into the use case. |
| 8 | Evaluation without snapshots → heuristic fallback, no error | **PASS** | use_cases.py:316-327: when `player_snaps` is empty, distributes `total_decks` across 4 days (even split + remainder). use_cases.py:310-311: if the snapshot query raises, it is swallowed (`except Exception: pass`) and the heuristic path is used. |
| 9 | `python scripts/snapshot_war.py --date ... --clan-tag ...` twice → idempotency | **FAIL** | Same root cause as AC2. `snapshot_war.py` → `collect_once` → `CollectSnapshotUseCase.execute` → `SqlWarSnapshotRepository.save` → `session.merge()` INSERT → `IntegrityError` on the second run for the same `(war_id, player_tag, snapshot_date)`. The CLI retry loop (snapshot_war.py:96-115) catches the exception and retries, but each retry hits the same IntegrityError, so all attempts fail and the script exits non-zero. |
| 10 | `grep -r "derive_per_day_attacks" backend/` → non-empty | **PASS** | Found in `backend/domain/model/aggregates.py` (definition, line 163) and `backend/application/port/primary/use_cases.py` (import + call, lines 285, 318). |

## Other checks

| Check | Verdict | Evidence |
|---|---|---|
| Frontend terminology ("Troféus" / "Pontos Hoje", no "Fama Total"/"Fama Hoje") | **PASS** | `frontend/src/pages/Dashboard.tsx` line 67 `label="Troféus"`, line 72 `label="Pontos Hoje"`. `grep -ri "fama total\|fama hoje" frontend/src/` → no matches (exit 1). |
| `npx tsc --noEmit` (frontend) | **PASS** | Exits 0, no type errors. |
| Python import check (all new modules) | **PASS** | `derive_per_day_attacks`, `CollectSnapshotUseCase`, `CheckCompletenessUseCase`, `EvaluateClanUseCase`, `SqlWarSnapshotRepository`, `SqlSnapshotRunRepository`, `router` all import cleanly. |
| Existing backend tests | **45 passed, 6 failed** | The 6 failures are pre-existing route tests in `tests/api/test_routes.py` failing with `ModuleNotFoundError: No module named 'asyncpg'` — a missing DB driver in this environment, not a code regression. |

## Issues found

### Issue 1 — CRITICAL: Idempotency broken (AC2, AC9 FAIL)

`SqlWarSnapshotRepository.save` (sql_repositories.py:296-311) relies on `session.merge(model)`
to upsert on the unique constraint `uq_warsnapshot_war_player_date`. However, the `WarSnapshotModel`
is constructed without a primary key (`id` left to autoincrement), and SQLAlchemy `merge` with
`id=None` performs an **INSERT**, not an upsert. On the second run for the same
`(war_id, player_tag, snapshot_date)`, the INSERT violates the unique constraint and raises
`IntegrityError`.

Verified empirically with an in-memory SQLite test reproducing the same pattern: first `merge`
inserts, second `merge` raises `UNIQUE constraint failed`.

Impact: the CLI double-run (AC9) and the use-case double-run (AC2) do not upsert — they crash.
The fix would be to use a proper upsert (e.g. PostgreSQL `INSERT ... ON CONFLICT (...) DO UPDATE`
via `sqlalchemy.dialects.postgresql.insert`, or load-then-update-or-insert within the session).

### Issue 2 — AC3 discrepancy: "ended" treated as active (PARTIAL FAIL)

use_cases.py:540 includes `"ended"` in the set of states that proceed to capture snapshots:
```python
if war_data is None or war_data.state not in ("active", "full", "warDay", "ended"):
```
AC3 requires `"ended" → no_war` with no player snapshots. The implementation captures snapshots
and logs `success` when `state == "ended"`. Only `"notInWar"` correctly maps to `no_war`.

Note: the plan (Boundary A) itself defines the no_war set as `∉ {active, warDay, full}`, i.e. it
excludes `"ended"` — so the implementation follows the plan but contradicts the spec AC3. This is
a spec-vs-plan inconsistency that needs resolution.

### Issue 3 — MISSING: All planned test files absent

The plan (Boundary E) specifies four test files. None of them exist:

- `backend/tests/application/test_collect_snapshots.py` — **MISSING** (the `tests/application/` directory is empty)
- `backend/tests/api/test_snapshot_routes.py` — **MISSING**
- `backend/tests/application/test_evaluate_with_snapshots.py` — **MISSING**
- `backend/tests/domain/test_derive_per_day_attacks.py` — **MISSING**

There are no happy-path or failure tests for `CollectSnapshotUseCase`,
`CheckCompletenessUseCase`, the snapshot HTTP endpoints, or `derive_per_day_attacks`. The DoD
verification command (`python -m pytest ...` for these four files) cannot run. This violates the
test-first/verifiable-DoD principle (Principle IV) and the QA scope requirement of at least one
happy-path and one failure test per use case.

### Issue 4 — AC5 caveat: today-count preferred over diff (design deviation)

`derive_per_day_attacks` (aggregates.py:211) uses `attacks = today if today > 0 else diff`,
preferring the API's `decksUsedToday` over the cumulative diff. The spec AC5 states the formula
`ataques_dia_2 = decksUsed_dia2 − decksUsed_dia1` unconditionally. The diff is only the fallback
path. This is a documented, intentional design decision (plan Boundary E: "today-count preferred
over diff") and is arguably more correct (the API's per-day count is authoritative), but it
deviates from the literal spec formula. Flagging for awareness; not blocking.

## Overall verdict

**FAIL**

Two acceptance criteria fail (AC2, AC9) due to a critical idempotency bug in the upsert
mechanism, and AC3 partially fails due to a spec-vs-plan inconsistency on the `"ended"` state.
Additionally, all four planned test files are missing, leaving the new use cases and the derive
function without any automated tests. The implementation cannot be considered Done.

Blocking issues: #1 (idempotency), #3 (missing tests). Non-blocking but needs resolution: #2
(ended state), #4 (today-count vs diff).
