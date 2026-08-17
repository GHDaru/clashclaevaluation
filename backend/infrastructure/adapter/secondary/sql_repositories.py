"""SQLAlchemy implementations of Repository ports."""

from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from application.port.secondary.repositories import (
    ClanRepository,
    PlayerRepository,
    PlayerWarRepository,
    SnapshotRunRepository,
    WarRepository,
    WarSnapshotRepository,
)
from domain.model.aggregates import PlayerWar, SnapshotRun, War, WarSnapshot, WarStatus
from domain.model.entities import Clan, Player
from domain.model.value_objects import (
    AttackCount,
    BlackCard,
    ClanTag,
    PlayerTag,
    RedCard,
    YellowCard,
)
from infrastructure.orm.models import (
    ClanModel,
    PlayerModel,
    PlayerWarModel,
    SnapshotRunModel,
    WarModel,
    WarSnapshotModel,
)


class SqlClanRepository(ClanRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_tag(self, tag: ClanTag) -> Clan | None:
        result = await self.session.get(ClanModel, str(tag))
        if result is None:
            return None
        return Clan(
            tag=ClanTag(result.tag),
            name=result.name,
            created_at=result.created_at,
            updated_at=result.updated_at,
        )

    async def save(self, clan: Clan) -> Clan:
        model = ClanModel(
            tag=str(clan.tag),
            name=clan.name,
            created_at=clan.created_at,
            updated_at=clan.updated_at,
        )
        await self.session.merge(model)
        await self.session.commit()
        return clan


class SqlPlayerRepository(PlayerRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_tag(self, tag: PlayerTag) -> Player | None:
        result = await self.session.get(PlayerModel, str(tag))
        if result is None:
            return None
        return Player(
            tag=PlayerTag(result.tag),
            name=result.name,
            role=result.role,
            first_seen=result.first_seen,
            last_seen=result.last_seen,
        )

    async def save(self, player: Player) -> Player:
        model = PlayerModel(
            tag=str(player.tag),
            clan_tag=None,
            name=player.name,
            role=player.role,
            first_seen=player.first_seen,
            last_seen=player.last_seen,
        )
        await self.session.merge(model)
        await self.session.commit()
        return player

    async def get_by_clan(self, clan_tag: ClanTag) -> list[Player]:
        result = await self.session.execute(
            select(PlayerModel)
        )
        return [
            Player(
                tag=PlayerTag(r.tag),
                name=r.name,
                role=r.role,
                first_seen=r.first_seen,
                last_seen=r.last_seen,
            )
            for r in result.scalars().all()
        ]


class SqlPlayerWarRepository(PlayerWarRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_war(self, war_id: int) -> list[PlayerWar]:
        result = await self.session.execute(
            select(PlayerWarModel).where(PlayerWarModel.war_id == war_id)
        )
        return [self._to_domain(r) for r in result.scalars().all()]

    async def get_by_player(
        self, tag: PlayerTag, limit: int = 12
    ) -> list[PlayerWar]:
        result = await self.session.execute(
            select(PlayerWarModel)
            .where(PlayerWarModel.player_tag == str(tag))
            .order_by(PlayerWarModel.created_at.desc())
            .limit(limit)
        )
        return [self._to_domain(r) for r in result.scalars().all()]

    def _to_domain(self, m: PlayerWarModel) -> PlayerWar:
        return PlayerWar(
            player_tag=PlayerTag(m.player_tag),
            player_name=m.player_name,
            attacks=[
                AttackCount(m.attacks_day1),
                AttackCount(m.attacks_day2),
                AttackCount(m.attacks_day3),
                AttackCount(m.attacks_day4),
            ],
            total_points=m.total_points,
            yellow_cards=YellowCard(m.yellow_cards),
            red_cards=RedCard(m.red_cards),
            black_cards=BlackCard(m.black_cards),
            incomplete=m.incomplete,
        )


class SqlWarRepository(WarRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, war_id: int) -> War | None:
        result = await self.session.get(WarModel, war_id)
        if result is None:
            return None
        return War(
            id=result.id,
            clan_tag=result.clan_tag,
            start_date=result.start_date,
            end_date=result.end_date,
            status=WarStatus(result.status),
            total_fame=result.total_fame,
            relaxed_days=result.relaxed_days,
            created_at=result.created_at,
        )

    async def get_by_clan_and_date(
        self, clan_tag: ClanTag, start_date: date
    ) -> War | None:
        result = await self.session.execute(
            select(WarModel)
            .where(
                WarModel.clan_tag == str(clan_tag),
                WarModel.start_date == start_date,
            )
            .order_by(WarModel.id.desc())
            .limit(1)
        )
        m = result.scalar_one_or_none()
        if m is None:
            return None
        return War(
            id=m.id,
            clan_tag=m.clan_tag,
            start_date=m.start_date,
            end_date=m.end_date,
            status=WarStatus(m.status),
            total_fame=m.total_fame,
            relaxed_days=m.relaxed_days,
            created_at=m.created_at,
        )

    async def get_recent(self, clan_tag: ClanTag, limit: int = 12) -> list[War]:
        result = await self.session.execute(
            select(WarModel)
            .where(WarModel.clan_tag == str(clan_tag))
            .order_by(WarModel.start_date.desc())
            .limit(limit)
        )
        return [
            War(
                id=m.id,
                clan_tag=m.clan_tag,
                start_date=m.start_date,
                end_date=m.end_date,
                status=WarStatus(m.status),
                total_fame=m.total_fame,
                relaxed_days=m.relaxed_days,
                created_at=m.created_at,
            )
            for m in result.scalars().all()
        ]

    async def save(self, war: War) -> War:
        # Upsert clan first to satisfy FK constraint
        clan_model = ClanModel(
            tag=war.clan_tag,
            name=war.clan_tag,
        )
        await self.session.merge(clan_model)

        # Upsert all players to satisfy FK constraint
        for pw in war.player_wars:
            player_model = PlayerModel(
                tag=str(pw.player_tag),
                clan_tag=war.clan_tag,
                name=pw.player_name,
                role="member",
            )
            await self.session.merge(player_model)

        await self.session.flush()

        model = WarModel(
            clan_tag=war.clan_tag,
            start_date=war.start_date,
            end_date=war.end_date,
            status=war.status.value,
            total_fame=war.total_fame,
            relaxed_days=war.relaxed_days,
        )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        war.id = model.id

        # Save player_wars
        for pw in war.player_wars:
            pw_model = PlayerWarModel(
                war_id=model.id,
                player_tag=str(pw.player_tag),
                player_name=pw.player_name,
                attacks_day1=pw.attacks[0].value,
                attacks_day2=pw.attacks[1].value,
                attacks_day3=pw.attacks[2].value,
                attacks_day4=pw.attacks[3].value,
                total_points=pw.total_points,
                yellow_cards=pw.yellow_cards.count,
                red_cards=pw.red_cards.count,
                black_cards=pw.black_cards.count,
                incomplete=pw.incomplete,
            )
            await self.session.merge(pw_model)

        await self.session.commit()
        return war


class SqlWarSnapshotRepository(WarSnapshotRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_war(self, war_id: int) -> list[WarSnapshot]:
        result = await self.session.execute(
            select(WarSnapshotModel)
            .where(WarSnapshotModel.war_id == war_id)
            .order_by(
                WarSnapshotModel.player_tag,
                WarSnapshotModel.snapshot_date,
            )
        )
        return [self._to_domain(r) for r in result.scalars().all()]

    async def get_by_war_and_player(
        self, war_id: int, player_tag: PlayerTag
    ) -> list[WarSnapshot]:
        result = await self.session.execute(
            select(WarSnapshotModel)
            .where(
                WarSnapshotModel.war_id == war_id,
                WarSnapshotModel.player_tag == str(player_tag),
            )
            .order_by(WarSnapshotModel.snapshot_date)
        )
        return [self._to_domain(r) for r in result.scalars().all()]

    async def save(self, snapshot: WarSnapshot) -> WarSnapshot:
        """Upsert a snapshot, idempotent on (war_id, player_tag, snapshot_date).

        Queries for an existing row by the unique constraint key. If found,
        updates it in place; otherwise inserts a new row. This avoids the
        IntegrityError that session.merge() with id=None would raise on the
        second run.
        """
        result = await self.session.execute(
            select(WarSnapshotModel).where(
                WarSnapshotModel.war_id == snapshot.war_id,
                WarSnapshotModel.player_tag == str(snapshot.player_tag),
                WarSnapshotModel.snapshot_date == snapshot.snapshot_date,
            )
        )
        existing = result.scalar_one_or_none()

        if existing is not None:
            # Update in place — true upsert
            existing.player_name = snapshot.player_name
            existing.decks_used_at_snapshot = snapshot.decks_used_at_snapshot
            existing.decks_used_today_at_snapshot = snapshot.decks_used_today_at_snapshot
            existing.fame_at_snapshot = snapshot.fame_at_snapshot
            existing.captured_at = snapshot.captured_at
        else:
            # Insert new
            model = WarSnapshotModel(
                war_id=snapshot.war_id,
                player_tag=str(snapshot.player_tag),
                player_name=snapshot.player_name,
                snapshot_date=snapshot.snapshot_date,
                decks_used_at_snapshot=snapshot.decks_used_at_snapshot,
                decks_used_today_at_snapshot=snapshot.decks_used_today_at_snapshot,
                fame_at_snapshot=snapshot.fame_at_snapshot,
                captured_at=snapshot.captured_at,
            )
            self.session.add(model)

        await self.session.commit()
        return snapshot

    def _to_domain(self, m: WarSnapshotModel) -> WarSnapshot:
        return WarSnapshot(
            war_id=m.war_id,
            player_tag=PlayerTag(m.player_tag),
            player_name=m.player_name,
            snapshot_date=m.snapshot_date,
            decks_used_at_snapshot=m.decks_used_at_snapshot,
            decks_used_today_at_snapshot=m.decks_used_today_at_snapshot,
            fame_at_snapshot=m.fame_at_snapshot,
            captured_at=m.captured_at,
        )


class SqlSnapshotRunRepository(SnapshotRunRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, run: SnapshotRun) -> SnapshotRun:
        model = SnapshotRunModel(
            war_id=run.war_id,
            clan_tag=run.clan_tag,
            snapshot_date=run.snapshot_date,
            status=run.status,
            participants_captured=run.participants_captured,
            error_message=run.error_message,
            triggered_by=run.triggered_by,
            captured_at=run.captured_at,
        )
        self.session.add(model)
        await self.session.commit()
        return run

    async def get_by_war(self, war_id: int) -> list[SnapshotRun]:
        result = await self.session.execute(
            select(SnapshotRunModel)
            .where(SnapshotRunModel.war_id == war_id)
            .order_by(SnapshotRunModel.snapshot_date)
        )
        return [self._to_domain(r) for r in result.scalars().all()]

    async def get_missing_dates(
        self, war_id: int, expected_dates: list[date]
    ) -> list[date]:
        """Return expected dates that have no successful snapshot run."""
        result = await self.session.execute(
            select(SnapshotRunModel.snapshot_date).where(
                SnapshotRunModel.war_id == war_id,
                SnapshotRunModel.status == "success",
            )
        )
        successful_dates = set(result.scalars().all())
        return [d for d in expected_dates if d not in successful_dates]

    def _to_domain(self, m: SnapshotRunModel) -> SnapshotRun:
        return SnapshotRun(
            war_id=m.war_id,
            clan_tag=m.clan_tag,
            snapshot_date=m.snapshot_date,
            status=m.status,
            participants_captured=m.participants_captured,
            error_message=m.error_message,
            triggered_by=m.triggered_by,
            captured_at=m.captured_at,
        )
