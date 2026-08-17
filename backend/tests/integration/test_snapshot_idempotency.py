"""Integration test: snapshot repository idempotency via upsert.

Uses in-memory SQLite to verify that saving the same snapshot twice
(war_id + player_tag + snapshot_date) updates the existing row instead
of raising an IntegrityError.
"""

from datetime import date, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from domain.model.aggregates import WarSnapshot
from domain.model.value_objects import PlayerTag
from infrastructure.adapter.secondary.sql_repositories import SqlWarSnapshotRepository
from infrastructure.orm.models import Base


@pytest.fixture
async def session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as s:
        yield s
    await engine.dispose()


class TestSnapshotIdempotency:
    TAG = PlayerTag("#ABC")
    SNAP_DATE = date(2026, 8, 14)

    def _make_snapshot(self, decks_used=4, decks_today=4, fame=1000):
        return WarSnapshot(
            war_id=1,
            player_tag=self.TAG,
            player_name="Player",
            snapshot_date=self.SNAP_DATE,
            decks_used_at_snapshot=decks_used,
            decks_used_today_at_snapshot=decks_today,
            fame_at_snapshot=fame,
            captured_at=datetime.utcnow(),
        )

    async def test_save_twice_updates_not_duplicates(self, session):
        """Saving the same snapshot twice results in one row, with the latest values."""
        repo = SqlWarSnapshotRepository(session)

        # First save
        snap1 = self._make_snapshot(decks_used=4, fame=1000)
        await repo.save(snap1)

        # Second save — different values, same key
        snap2 = self._make_snapshot(decks_used=7, fame=2000)
        await repo.save(snap2)

        # Should have exactly one snapshot for this war/player/date
        all_snaps = await repo.get_by_war(1)
        assert len(all_snaps) == 1, f"Expected 1 snapshot, got {len(all_snaps)}"
        assert all_snaps[0].decks_used_at_snapshot == 7
        assert all_snaps[0].fame_at_snapshot == 2000

    async def test_different_dates_create_separate_rows(self, session):
        """Snapshots on different dates are separate rows."""
        repo = SqlWarSnapshotRepository(session)

        await repo.save(self._make_snapshot(decks_used=4))
        snap_day2 = WarSnapshot(
            war_id=1,
            player_tag=self.TAG,
            player_name="Player",
            snapshot_date=date(2026, 8, 15),
            decks_used_at_snapshot=7,
            decks_used_today_at_snapshot=3,
            fame_at_snapshot=2000,
            captured_at=datetime.utcnow(),
        )
        await repo.save(snap_day2)

        all_snaps = await repo.get_by_war(1)
        assert len(all_snaps) == 2

    async def test_different_players_create_separate_rows(self, session):
        """Snapshots for different players are separate rows."""
        repo = SqlWarSnapshotRepository(session)

        await repo.save(self._make_snapshot(decks_used=4))
        snap_p2 = WarSnapshot(
            war_id=1,
            player_tag=PlayerTag("#XYZ"),
            player_name="Player2",
            snapshot_date=self.SNAP_DATE,
            decks_used_at_snapshot=3,
            decks_used_today_at_snapshot=3,
            fame_at_snapshot=800,
            captured_at=datetime.utcnow(),
        )
        await repo.save(snap_p2)

        all_snaps = await repo.get_by_war(1)
        assert len(all_snaps) == 2
