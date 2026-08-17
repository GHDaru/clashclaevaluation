# Contracts — Spec 008 (Daily War Snapshots)

- **Spec**: `spec.md` · **Date**: 2026-08-17

> Interfaces between parts introduced or touched by this cycle: the collection use case port,
> the two primary adapters (CLI + HTTP), and the evaluation-integration seam.

## 1. Collection use case (primary port)

```
CollectSnapshotsUseCase.execute(command: CollectSnapshotsCommand) -> CollectSnapshotsResultDTO

CollectSnapshotsCommand:
  clan_tag: str            # e.g. "#QPUJC0CG"
  snapshot_date: date | None   # None ⇒ today (UTC); explicit for backfill
  triggered_by: str = "cron"   # "cron" | "manual"

CollectSnapshotsResultDTO:
  war_id: int | None
  snapshot_date: str           # ISO
  status: str                  # "success" | "failure" | "no_war"
  participants_captured: int
  error: str | None
```

Dependencies (injected): `CRApiClient`, `WarRepository`, `WarSnapshotRepository`,
`SnapshotRunRepository`. Idempotent: re-running for the same `(war_id, player_tag, date)`
upserts (unique constraint `uq_warsnapshot_war_player_date`); exactly one `SnapshotRun` row per
execution (a failure run does not coexist with a success run for the same execution — FR/DoD).

## 2. CLI primary adapter — `scripts/snapshot_war.py`

```
python scripts/snapshot_war.py [--date YYYY-MM-DD] [--clan-tag "#TAG"]
```

- `--date` defaults to today (UTC). `--clan-tag` defaults to `settings.cr_clan_tag`.
- Retry: limited attempts (e.g. 3) with exponential backoff when the use case returns
  `status="failure"` (API unavailable). A `no_war` status is terminal (not retried).
- Exit code: 0 on success/no_war, non-zero on failure. Logs to stdout (structured enough for
  cron capture). Builds its own async DI (reuses `application.di` factories + async session).
- Cron expression (ops-owned, documented here): `30 5 * * 4-7` (05:30 UTC Thu–Sun).

## 3. HTTP primary adapter — FastAPI routes (`backend/infrastructure/adapter/primary/fastapi_routes.py`)

```
POST /api/v1/snapshots/collect
  body: { "snapshot_date": "YYYY-MM-DD" | null }   # null ⇒ today
  → 200 { war_id, snapshot_date, status, participants_captured, error }
  (triggered_by="manual")

GET /api/v1/snapshots/missing
  query: clan_tag (defaults to settings.cr_clan_tag)
  → 200 { war_id, war_start_date, expected_dates: [...], missing_dates: [...] }
```

`missing` computes the 4 expected war days (Thu–Sun from the current war's start date) and
returns those with no successful `SnapshotRun`, via `SnapshotRunRepository.get_missing_dates`.

## 4. Evaluation integration seam (`EvaluateClanUseCase`)

New dependency: `WarSnapshotRepository`. After resolving `war_id` for the current war:

- Fetch `snapshots = war_snapshot_repo.get_by_war(war_id)`.
- Group by `player_tag`. For each participant with snapshots, build
  `attacks = derive_per_day_attacks(player_snapshots, war_start_date)`.
- Participants **without** snapshots ⇒ current even-distribution heuristic (fallback, FR7).
- No snapshots at all for the war ⇒ pure fallback (current behaviour, unchanged).

No change to `EvaluationService` or domain contracts — only the `attacks` list fed into
`PlayerWar` changes source.

## 5. DI wiring (`backend/application/di.py`)

Add: `get_war_snapshot_repo()`, `get_snapshot_run_repo()`, `get_collect_snapshots_use_case()`;
extend `get_evaluate_use_case()` to pass `get_war_snapshot_repo()`.
