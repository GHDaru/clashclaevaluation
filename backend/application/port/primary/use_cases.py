"""Primary Ports — use cases (what the system DOES).

Application services that orchestrate domain services + secondary ports.
"""

from dataclasses import dataclass
from datetime import date, datetime

from application.port.secondary.cr_api_client import CRApiClient
from application.port.secondary.repositories import (
    PlayerRepository,
    PlayerWarRepository,
    SnapshotRunRepository,
    WarRepository,
    WarSnapshotRepository,
)
from domain.model.aggregates import PlayerStatus, SnapshotRun, Trend, WarSnapshot, WarStatus
from domain.model.value_objects import ClanTag, PlayerTag
from domain.service.evaluation import EvaluationConfig, EvaluationService
from domain.service.relaxation import RelaxationService


@dataclass
class ClanStatusDTO:
    war_active: bool
    war_id: int | None
    day: int | None
    day_label: str | None
    status: str | None
    position: int | None
    total_fame: int
    daily_fame: int
    clans_count: int
    relaxed: bool
    players: list["PlayerStatusDTO"]


@dataclass
class PlayerStatusDTO:
    tag: str
    name: str
    role: str
    attacks_today: int
    attacks_total: int
    total_points: int
    yellow_cards: int
    red_cards: int
    black_cards: int
    status: str
    trend: str
    in_clan: bool


@dataclass
class PlayerHistoryDTO:
    tag: str
    name: str
    role: str
    first_seen: str
    last_seen: str
    current_war: dict | None
    recency: dict
    history: list[dict]


@dataclass
class EvaluateCommand:
    clan_tag: str
    triggered_by: str = "manual"


@dataclass
class SnapshotResultDTO:
    status: str  # "success", "failure", "no_war"
    war_id: int | None
    participants_captured: int
    snapshot_date: str
    error: str | None = None


@dataclass
class CompletenessResultDTO:
    war_id: int | None
    expected_dates: list[str]
    missing_dates: list[str]
    is_complete: bool


@dataclass
class EvaluateResultDTO:
    war_id: int
    evaluated_at: str
    players_evaluated: int
    summary: dict


class GetClanStatusUseCase:
    """Returns the current War status for the whole clan."""

    def __init__(
        self,
        war_repo: WarRepository,
        player_war_repo: PlayerWarRepository,
        cr_api: CRApiClient,
        config: EvaluationConfig,
    ):
        self.war_repo = war_repo
        self.player_war_repo = player_war_repo
        self.cr_api = cr_api
        self.config = config

    async def execute(self, clan_tag: ClanTag) -> ClanStatusDTO:
        war_data = await self.cr_api.get_current_war(clan_tag)

        if war_data is None or war_data.state not in ("active", "ended", "full", "warDay"):
            return ClanStatusDTO(
                war_active=False,
                war_id=None,
                day=None,
                day_label=None,
                status=None,
                position=None,
                total_fame=0,
                daily_fame=0,
                clans_count=0,
                relaxed=False,
                players=[],
            )

        day_labels = ["Quinta", "Sexta", "Sábado", "Domingo"]

        # Try to find persisted war for additional data
        from datetime import date, timedelta

        today = date.today()
        start_date = today - timedelta(days=today.weekday() - 3)  # Thursday of this week
        if today.weekday() < 3:  # Before Thursday
            start_date = start_date - timedelta(weeks=1)

        # Calculate day within the war (0-3 for Thu-Sun) from current weekday,
        # not from periodIndex (which is cumulative across the season)
        if 3 <= today.weekday() <= 6:  # Thu=3 .. Sun=6
            day = today.weekday() - 3
        else:
            day = war_data.period_index if 0 <= war_data.period_index < 4 else 0
        day_label = day_labels[day] if 0 <= day < 4 else None

        war = await self.war_repo.get_by_clan_and_date(clan_tag, start_date)
        war_id = war.id if war else None
        relaxed = war.is_day_relaxed(day) if war else False

        # Fetch current clan members to distinguish active members from ex-members
        try:
            member_tags = set(await self.cr_api.get_clan_members(clan_tag))
        except Exception:
            member_tags = None  # API unavailable — don't mark anyone as ex-member

        # Build player status from API participants
        players: list[PlayerStatusDTO] = []

        for p in war_data.participants:
            attacks_today = p.decks_used_today
            attacks_total = p.decks_used

            # Quick card calc for display (without full war aggregate)
            missing_today = max(0, self.config.attacks_per_day - attacks_today)
            yellow = missing_today
            red = 0
            black = 0

            if yellow >= self.config.yellow_to_red:
                red = yellow // self.config.yellow_to_red
                yellow = yellow % self.config.yellow_to_red
            if red >= self.config.red_to_black:
                black = red // self.config.red_to_black
                red = red % self.config.red_to_black

            if black > 0:
                status = PlayerStatus.CRITICAL.value
            elif red > 0:
                status = PlayerStatus.DANGER.value
            elif yellow > 0:
                status = PlayerStatus.WARNING.value
            else:
                status = PlayerStatus.CLEAN.value

            in_clan = member_tags is None or p.tag in member_tags

            players.append(
                PlayerStatusDTO(
                    tag=p.tag,
                    name=p.name,
                    role="member",
                    attacks_today=attacks_today,
                    attacks_total=attacks_total,
                    total_points=p.fame,
                    yellow_cards=yellow,
                    red_cards=red,
                    black_cards=black,
                    status=status,
                    trend=Trend.STABLE.value,
                    in_clan=in_clan,
                )
            )

        # Calculate clan placement from competing clans sorted by fame
        clans_count = len(war_data.clans)
        placement = None
        if clans_count > 0:
            sorted_clans = sorted(war_data.clans, key=lambda c: c.fame, reverse=True)
            for i, c in enumerate(sorted_clans):
                if c.tag == str(clan_tag):
                    placement = i + 1
                    break

        return ClanStatusDTO(
            war_active=war_data.state in ("active", "full", "warDay"),
            war_id=war_id,
            day=day,
            day_label=day_label,
            status=war_data.state,
            position=placement,
            total_fame=war_data.clan_score,
            daily_fame=war_data.clan_fame,
            clans_count=clans_count,
            relaxed=relaxed,
            players=players,
        )


class EvaluateClanUseCase:
    """Triggers an Evaluation for the current War."""

    def __init__(
        self,
        war_repo: WarRepository,
        player_war_repo: PlayerWarRepository,
        cr_api: CRApiClient,
        evaluation_service: EvaluationService,
        relaxation_service: RelaxationService,
        snapshot_repo: WarSnapshotRepository | None = None,
    ):
        self.war_repo = war_repo
        self.player_war_repo = player_war_repo
        self.cr_api = cr_api
        self.evaluation_service = evaluation_service
        self.relaxation_service = relaxation_service
        self.snapshot_repo = snapshot_repo

    async def execute(self, command: EvaluateCommand) -> EvaluateResultDTO:
        clan_tag = ClanTag(command.clan_tag)
        war_data = await self.cr_api.get_current_war(clan_tag)

        if war_data is None:
            return EvaluateResultDTO(
                war_id=0,
                evaluated_at=datetime.utcnow().isoformat(),
                players_evaluated=0,
                summary={"error": "No active war"},
            )

        from datetime import date, timedelta

        today = date.today()
        start_date = today - timedelta(days=today.weekday() - 3)
        if today.weekday() < 3:
            start_date = start_date - timedelta(weeks=1)
        end_date = start_date + timedelta(days=3)

        # Determine war status
        status_map = {
            "active": WarStatus.FINISHED_1ST,  # Default; will be refined
            "ended": WarStatus.FINISHED_1ST,
        }
        status = status_map.get(war_data.state, WarStatus.FINISHED_1ST)

        # Compute relaxed days
        relaxed_days: list[int] = []
        if war_data.state == "ended":
            # If clan finished 1st, remaining days after periodIndex are relaxed
            for i in range(war_data.period_index + 1, 4):
                relaxed_days.append(i)

        # Build War aggregate
        from domain.model.aggregates import PlayerWar, War, derive_per_day_attacks
        from domain.model.value_objects import AttackCount

        war = War(
            id=None,
            clan_tag=command.clan_tag,
            start_date=start_date,
            end_date=end_date,
            status=status,
            total_fame=war_data.clan_score,
            relaxed_days=relaxed_days,
        )

        # Try to load snapshots for real per-day attack counts
        snapshot_map: dict[str, list] = {}
        if self.snapshot_repo is not None:
            try:
                existing_war = await self.war_repo.get_by_clan_and_date(
                    ClanTag(command.clan_tag), start_date
                )
                if existing_war is not None:
                    all_snaps = await self.snapshot_repo.get_by_war(existing_war.id)
                    for snap in all_snaps:
                        tag_key = str(snap.player_tag)
                        snapshot_map.setdefault(tag_key, []).append(snap)
            except Exception:
                pass  # Snapshot query failed — use heuristic fallback

        for p in war_data.participants:
            player_snaps = snapshot_map.get(p.tag, [])

            if player_snaps:
                # Real per-day attacks from snapshot diffs
                attacks = derive_per_day_attacks(player_snaps, start_date)
            else:
                # Heuristic fallback: distribute total decks evenly across days
                total_decks = p.decks_used
                attacks_per_day_avg = total_decks // 4 if total_decks > 0 else 0
                remainder = total_decks % 4 if total_decks > 0 else 0
                attacks = []
                for i in range(4):
                    val = attacks_per_day_avg + (1 if i < remainder else 0)
                    attacks.append(AttackCount(min(4, val)))

            pw = PlayerWar(
                player_tag=PlayerTag(p.tag),
                player_name=p.name,
                attacks=attacks,
                total_points=p.fame,
            )
            war.add_player_war(pw)

        # Evaluate
        results = self.evaluation_service.evaluate(war)

        # Persist
        saved_war = await self.war_repo.save(war)

        summary = {
            "total_players": len(results),
            "clean": sum(
                1 for r in results
                if r.final_black == 0 and r.final_red == 0 and r.final_yellow == 0
            ),
            "warning": sum(1 for r in results if r.final_yellow > 0 and r.final_black == 0),
            "danger": sum(1 for r in results if r.final_red > 0 and r.final_black == 0),
            "critical": sum(1 for r in results if r.final_black > 0),
        }

        return EvaluateResultDTO(
            war_id=saved_war.id or 0,
            evaluated_at=datetime.utcnow().isoformat(),
            players_evaluated=len(results),
            summary=summary,
        )


class GetPlayerHistoryUseCase:
    """Returns a player's history: current War + recency + expandable history.

    Falls back to the CR API for player info when not yet persisted.
    Also enriches with real-time current-war data from the clan's River Race.
    """

    def __init__(
        self,
        player_repo: PlayerRepository,
        player_war_repo: PlayerWarRepository,
        cr_api: CRApiClient,
        clan_tag: str,
        config: EvaluationConfig,
    ):
        self.player_repo = player_repo
        self.player_war_repo = player_war_repo
        self.cr_api = cr_api
        self.clan_tag = clan_tag
        self.config = config

    async def execute(
        self, tag: PlayerTag, expand: bool = False
    ) -> PlayerHistoryDTO:
        player = await self.player_repo.get_by_tag(tag)

        # Fallback: fetch player info from CR API if not in DB
        if player is None:
            try:
                info = await self.cr_api.get_player(tag)
                from domain.model.entities import Player
                from datetime import datetime
                now = datetime.now()
                player = Player(
                    tag=tag,
                    name=info.name,
                    role=info.role,
                    first_seen=now,
                    last_seen=now,
                )
            except Exception:
                return PlayerHistoryDTO(
                    tag=str(tag),
                    name="Unknown",
                    role="member",
                    first_seen="",
                    last_seen="",
                    current_war=None,
                    recency={"wars": []},
                    history=[],
                )

        # Get recent player wars from DB
        limit = 12 if expand else 4
        player_wars = await self.player_war_repo.get_by_player(tag, limit=limit)

        history = []
        for pw in player_wars:
            history.append({
                "war_id": None,
                "yellow": pw.yellow_cards.count,
                "red": pw.red_cards.count,
                "black": pw.black_cards.count,
                "total_attacks": pw.total_attacks,
                "total_points": pw.total_points,
                "status": pw.status.value,
            })

        # Enrich with real-time current war data from CR API
        current_war = history[0] if history else None
        try:
            war_data = await self.cr_api.get_current_war(ClanTag(self.clan_tag))
            if war_data and war_data.state in ("active", "full", "warDay"):
                for p in war_data.participants:
                    if p.tag == str(tag):
                        missing = max(0, self.config.attacks_per_day - p.decks_used_today)
                        yellow = missing
                        red = 0
                        black = 0
                        if yellow >= self.config.yellow_to_red:
                            red = yellow // self.config.yellow_to_red
                            yellow = yellow % self.config.yellow_to_red
                        if red >= self.config.red_to_black:
                            black = red // self.config.red_to_black
                            red = red % self.config.red_to_black

                        if black > 0:
                            rt_status = PlayerStatus.CRITICAL.value
                        elif red > 0:
                            rt_status = PlayerStatus.DANGER.value
                        elif yellow > 0:
                            rt_status = PlayerStatus.WARNING.value
                        else:
                            rt_status = PlayerStatus.CLEAN.value

                        current_war = {
                            "war_id": None,
                            "yellow": yellow,
                            "red": red,
                            "black": black,
                            "total_attacks": p.decks_used,
                            "total_points": p.fame,
                            "attacks_today": p.decks_used_today,
                            "status": rt_status,
                        }
                        break
        except Exception:
            pass  # CR API unavailable — use DB history only

        # Recency = last 4 weeks
        recency_wars = history[:4]
        trend = Trend.STABLE.value
        if len(recency_wars) >= 2:
            recent_yellows = sum(w["yellow"] for w in recency_wars[:2])
            older_yellows = sum(w["yellow"] for w in recency_wars[2:4])
            if recent_yellows < older_yellows:
                trend = Trend.IMPROVING.value
            elif recent_yellows > older_yellows:
                trend = Trend.DECLINING.value

        return PlayerHistoryDTO(
            tag=str(tag),
            name=player.name,
            role=player.role,
            first_seen=player.first_seen.isoformat() if player.first_seen else "",
            last_seen=player.last_seen.isoformat() if player.last_seen else "",
            current_war=current_war,
            recency={"wars": recency_wars, "trend": trend},
            history=history,
        )


class CollectSnapshotUseCase:
    """Captures a daily snapshot of war progress for all participants.

    Fetches the current war data from the CR API, upserts a snapshot per
    participant, and logs the run for auditability. Idempotent: re-running
    for the same war/player/date updates the existing snapshot (upsert).
    """

    def __init__(
        self,
        war_repo: WarRepository,
        snapshot_repo: WarSnapshotRepository,
        run_repo: SnapshotRunRepository,
        cr_api: CRApiClient,
    ):
        self.war_repo = war_repo
        self.snapshot_repo = snapshot_repo
        self.run_repo = run_repo
        self.cr_api = cr_api

    async def execute(
        self,
        clan_tag: ClanTag,
        snapshot_date: date | None = None,
        triggered_by: str = "cron",
    ) -> SnapshotResultDTO:
        from datetime import date as date_cls, datetime, timedelta

        if snapshot_date is None:
            snapshot_date = date_cls.today()

        try:
            war_data = await self.cr_api.get_current_war(clan_tag)
        except Exception as e:
            await self._log_run(
                None, str(clan_tag), snapshot_date, "failure",
                0, str(e)[:500], triggered_by,
            )
            return SnapshotResultDTO(
                status="failure",
                war_id=None,
                participants_captured=0,
                snapshot_date=snapshot_date.isoformat(),
                error=str(e)[:500],
            )

        if war_data is None or war_data.state not in ("active", "full", "warDay"):
            await self._log_run(
                None, str(clan_tag), snapshot_date, "no_war",
                0, None, triggered_by,
            )
            return SnapshotResultDTO(
                status="no_war",
                war_id=None,
                participants_captured=0,
                snapshot_date=snapshot_date.isoformat(),
            )

        # Find or create the war record
        today = date_cls.today()
        start_date = today - timedelta(days=today.weekday() - 3)
        if today.weekday() < 3:
            start_date = start_date - timedelta(weeks=1)
        end_date = start_date + timedelta(days=3)

        war = await self.war_repo.get_by_clan_and_date(clan_tag, start_date)
        war_id = war.id if war else None

        if war_id is None:
            # Create a minimal war record so snapshots have an FK target
            from domain.model.aggregates import War
            war = War(
                id=None,
                clan_tag=str(clan_tag),
                start_date=start_date,
                end_date=end_date,
                status=WarStatus.FINISHED_1ST,
                total_fame=war_data.clan_score,
                relaxed_days=[],
            )
            saved_war = await self.war_repo.save(war)
            war_id = saved_war.id

        # Upsert a snapshot per participant
        now = datetime.utcnow()
        captured = 0
        for p in war_data.participants:
            snapshot = WarSnapshot(
                war_id=war_id,
                player_tag=PlayerTag(p.tag),
                player_name=p.name,
                snapshot_date=snapshot_date,
                decks_used_at_snapshot=p.decks_used,
                decks_used_today_at_snapshot=p.decks_used_today,
                fame_at_snapshot=p.fame,
                captured_at=now,
            )
            await self.snapshot_repo.save(snapshot)
            captured += 1

        await self._log_run(
            war_id, str(clan_tag), snapshot_date, "success",
            captured, None, triggered_by,
        )

        return SnapshotResultDTO(
            status="success",
            war_id=war_id,
            participants_captured=captured,
            snapshot_date=snapshot_date.isoformat(),
        )

    async def _log_run(
        self,
        war_id: int | None,
        clan_tag: str,
        snapshot_date: date,
        status: str,
        participants: int,
        error: str | None,
        triggered_by: str,
    ) -> None:
        from datetime import datetime
        run = SnapshotRun(
            war_id=war_id,
            clan_tag=clan_tag,
            snapshot_date=snapshot_date,
            status=status,
            participants_captured=participants,
            error_message=error,
            triggered_by=triggered_by,
            captured_at=datetime.utcnow(),
        )
        await self.run_repo.save(run)


class CheckCompletenessUseCase:
    """Detects war days that are missing snapshots."""

    def __init__(
        self,
        war_repo: WarRepository,
        run_repo: SnapshotRunRepository,
    ):
        self.war_repo = war_repo
        self.run_repo = run_repo

    async def execute(self, clan_tag: ClanTag) -> CompletenessResultDTO:
        from datetime import date as date_cls, timedelta

        today = date_cls.today()
        start_date = today - timedelta(days=today.weekday() - 3)
        if today.weekday() < 3:
            start_date = start_date - timedelta(weeks=1)

        expected_dates = [start_date + timedelta(days=i) for i in range(4)]

        war = await self.war_repo.get_by_clan_and_date(clan_tag, start_date)
        if war is None:
            return CompletenessResultDTO(
                war_id=None,
                expected_dates=[d.isoformat() for d in expected_dates],
                missing_dates=[d.isoformat() for d in expected_dates],
                is_complete=False,
            )

        missing = await self.run_repo.get_missing_dates(war.id, expected_dates)
        return CompletenessResultDTO(
            war_id=war.id,
            expected_dates=[d.isoformat() for d in expected_dates],
            missing_dates=[d.isoformat() for d in missing],
            is_complete=len(missing) == 0,
        )
