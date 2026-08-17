"""Standalone daily snapshot collector for ClashClanEvaluation.

Runs via cron (05:30 UTC Thu-Sun) or manually for backfill. Fetches the
current River Race data from the Clash Royale API, upserts a snapshot per
participant, and logs the run for auditability.

Usage:
    # Cron (auto-detects today's date, uses configured clan tag):
    python -m scripts.snapshot_war

    # Manual backfill for a specific date and clan:
    python -m scripts.snapshot_war --date 2026-08-14 --clan-tag "#QPUJC0CG"

    # With explicit retry count:
    python -m scripts.snapshot_war --retries 3

Cron entry (crontab -e):
    30 5 * * 4-7 cd /path/to/backend && python -m scripts.snapshot_war >> /var/log/snapshots.log 2>&1
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from datetime import date
from pathlib import Path

# Ensure backend/ is on sys.path when run as a script
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from application.port.primary.use_cases import CollectSnapshotUseCase
from domain.model.value_objects import ClanTag
from infrastructure.adapter.secondary.cr_http_client import HttpCRApiClient
from infrastructure.adapter.secondary.sql_repositories import (
    SqlSnapshotRunRepository,
    SqlWarRepository,
    SqlWarSnapshotRepository,
)
from infrastructure.config import settings
from infrastructure.orm.database import async_session

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("snapshot_war")

MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 30


async def collect_once(
    clan_tag: ClanTag,
    snapshot_date: date | None,
    triggered_by: str,
) -> str:
    """Run one collection attempt. Returns the status string."""
    session = async_session()
    try:
        use_case = CollectSnapshotUseCase(
            war_repo=SqlWarRepository(session),
            snapshot_repo=SqlWarSnapshotRepository(session),
            run_repo=SqlSnapshotRunRepository(session),
            cr_api=HttpCRApiClient(),
        )
        result = await use_case.execute(
            clan_tag,
            snapshot_date=snapshot_date,
            triggered_by=triggered_by,
        )
        logger.info(
            "Snapshot %s: status=%s, war_id=%s, participants=%d",
            result.snapshot_date,
            result.status,
            result.war_id,
            result.participants_captured,
        )
        if result.error:
            logger.error("Error: %s", result.error)
        return result.status
    finally:
        await session.close()


async def collect_with_retry(
    clan_tag: ClanTag,
    snapshot_date: date | None,
    triggered_by: str,
    max_retries: int,
) -> int:
    """Retry on failure with exponential backoff. Returns exit code."""
    import asyncio as aio

    for attempt in range(1, max_retries + 1):
        try:
            status = await collect_once(clan_tag, snapshot_date, triggered_by)
            if status == "success":
                return 0
            if status == "no_war":
                logger.info("No active war — nothing to capture.")
                return 0
            # failure — retry
            logger.warning("Attempt %d/%d failed, retrying...", attempt, max_retries)
        except Exception as e:
            logger.exception("Attempt %d/%d raised: %s", attempt, max_retries, e)

        if attempt < max_retries:
            delay = RETRY_DELAY_SECONDS * attempt
            logger.info("Waiting %ds before retry...", delay)
            await aio.sleep(delay)

    logger.error("All %d attempts failed.", max_retries)
    return 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect daily war snapshots from the Clash Royale API."
    )
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="Snapshot date in YYYY-MM-DD format (default: today).",
    )
    parser.add_argument(
        "--clan-tag",
        type=str,
        default=None,
        help='Clan tag (e.g. "#QPUJC0CG"). Defaults to CR_CLAN_TAG from config.',
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=MAX_RETRIES,
        help=f"Max retry attempts on failure (default: {MAX_RETRIES}).",
    )
    parser.add_argument(
        "--manual",
        action="store_true",
        help="Mark this run as manually triggered (for audit log).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    # Resolve clan tag
    clan_tag_str = args.clan_tag or settings.cr_clan_tag
    if not clan_tag_str:
        logger.error("No clan tag provided. Use --clan-tag or set CR_CLAN_TAG in config.")
        return 2
    if not clan_tag_str.startswith("#"):
        clan_tag_str = f"#{clan_tag_str}"

    try:
        clan_tag = ClanTag(clan_tag_str)
    except ValueError as e:
        logger.error("Invalid clan tag: %s", e)
        return 2

    # Resolve snapshot date
    snapshot_date = None
    if args.date:
        try:
            snapshot_date = date.fromisoformat(args.date)
        except ValueError:
            logger.error("Invalid date format: %s (use YYYY-MM-DD)", args.date)
            return 2

    triggered_by = "manual" if args.manual else "cron"

    logger.info(
        "Starting snapshot collection: clan=%s, date=%s, triggered_by=%s",
        clan_tag,
        snapshot_date or "today",
        triggered_by,
    )

    exit_code = asyncio.run(
        collect_with_retry(
            clan_tag,
            snapshot_date,
            triggered_by,
            args.retries,
        )
    )
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
