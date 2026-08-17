"""Aggregates — cluster of entities with a root that guarantees consistency."""

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import StrEnum

from domain.model.value_objects import (
    AttackCount,
    BlackCard,
    CardSummary,
    PlayerTag,
    RedCard,
    WarDay,
    YellowCard,
)


class WarStatus(StrEnum):
    FINISHED_1ST = "finished_1st"
    FINISHED_2ND = "finished_2nd"
    FINISHED_3RD = "finished_3rd"
    FINISHED_4TH = "finished_4th"
    FINISHED_5TH = "finished_5th"


class PlayerStatus(StrEnum):
    CLEAN = "clean"
    WARNING = "warning"
    DANGER = "danger"
    CRITICAL = "critical"


class Trend(StrEnum):
    IMPROVING = "improving"
    STABLE = "stable"
    DECLINING = "declining"
    NEW = "new"


@dataclass
class PlayerWar:
    """A player's participation in one specific War.
    Part of the War aggregate — War is the aggregate root."""

    player_tag: PlayerTag
    player_name: str
    attacks: list[AttackCount]  # [day1, day2, day3, day4]
    total_points: int
    yellow_cards: YellowCard = field(default_factory=lambda: YellowCard(0))
    red_cards: RedCard = field(default_factory=lambda: RedCard(0))
    black_cards: BlackCard = field(default_factory=lambda: BlackCard(0))
    incomplete: bool = False

    @property
    def total_attacks(self) -> int:
        return sum(a.value for a in self.attacks)

    @property
    def total_missing(self) -> int:
        return sum(a.missing for a in self.attacks)

    @property
    def status(self) -> PlayerStatus:
        if self.black_cards.count > 0:
            return PlayerStatus.CRITICAL
        if self.red_cards.count > 0:
            return PlayerStatus.DANGER
        if self.yellow_cards.count > 0:
            return PlayerStatus.WARNING
        return PlayerStatus.CLEAN

    @property
    def card_summary(self) -> CardSummary:
        return CardSummary(
            yellow=self.yellow_cards.count,
            red=self.red_cards.count,
            black=self.black_cards.count,
        )


@dataclass
class War:
    """A War (Guerra) — the aggregate root for a weekly clan war cycle.
    Owns PlayerWar records and enforces consistency boundaries."""

    id: int | None  # None before persistence
    clan_tag: str
    start_date: date  # Thursday
    end_date: date  # Sunday
    status: WarStatus
    total_fame: int
    relaxed_days: list[int]  # indices of relaxed WarDays (empty if none)
    player_wars: list[PlayerWar] = field(default_factory=list)
    created_at: datetime | None = None

    @property
    def war_days(self) -> list[WarDay]:
        return WarDay.all_days()

    @property
    def has_early_victory(self) -> bool:
        """EarlyVictory: clan finished 1st before Sunday (index 3)."""
        return self.status == WarStatus.FINISHED_1ST and len(self.relaxed_days) > 0

    def is_day_relaxed(self, day_index: int) -> bool:
        return day_index in self.relaxed_days

    def add_player_war(self, player_war: PlayerWar) -> None:
        self.player_wars.append(player_war)

    def get_player_war(self, tag: PlayerTag) -> PlayerWar | None:
        for pw in self.player_wars:
            if pw.player_tag == tag:
                return pw
        return None


@dataclass
class WarSnapshot:
    """A point-in-time capture of a player's cumulative war progress.

    The Clash Royale API exposes only cumulative counters (decksUsed,
    decksUsedToday, fame) with no per-day breakdown. By storing one
    snapshot per war-day and diffing consecutive snapshots, per-day
    attack counts can be reconstructed:

        attacks_on_day_X = decks_used_at_snapshot(day_X)
                          - decks_used_at_snapshot(day_X-1)

    For a player's first snapshot (no prior), the prior cumulative is
    treated as 0. This naturally handles players joining mid-war.

    Part of the War aggregate — War is the aggregate root.
    """

    war_id: int
    player_tag: PlayerTag
    player_name: str
    snapshot_date: date
    # Cumulative decksUsed from API (0-16 over the full war)
    decks_used_at_snapshot: int
    # decksUsedToday from API (0-4) — cross-check for the diff
    decks_used_today_at_snapshot: int
    # Cumulative fame from API
    fame_at_snapshot: int
    captured_at: datetime | None = None

    def attacks_since(self, prior: "WarSnapshot | None") -> int:
        """Attacks performed between the prior snapshot and this one.

        If *prior* is ``None`` the player had no earlier snapshot (first
        capture, or joined mid-war) so the full cumulative is returned.
        """
        prior_decks = prior.decks_used_at_snapshot if prior else 0
        return self.decks_used_at_snapshot - prior_decks

    def fame_since(self, prior: "WarSnapshot | None") -> int:
        """Fame earned between the prior snapshot and this one."""
        prior_fame = prior.fame_at_snapshot if prior else 0
        return self.fame_at_snapshot - prior_fame


def derive_per_day_attacks(
    snapshots: list[WarSnapshot],
    war_start_date: date,
) -> list[AttackCount]:
    """Derive per-day attack counts (day1..day4) from snapshots.

    *snapshots* must all belong to the same player and the same war.
    They are sorted internally by ``snapshot_date``.

    Each war day is Thursday→Sunday (offset 0-3 from *war_start_date*).

    Strategy:
      1. When a snapshot exists for a day, prefer ``decks_used_today_at_snapshot``
         (the API's own per-day count) as the authoritative value.
      2. Fall back to the cumulative diff (``decks_used_at_snapshot`` minus
         the prior snapshot's cumulative) when the API's today-count is 0
         but the diff is positive — this catches edge cases where the API
         resets ``decksUsedToday`` before we capture the snapshot.
      3. Days with no snapshot default to 0 attacks.

    If a snapshot is missing for a day, the cumulative diff "rolls forward"
    to the next available snapshot. Because ``decks_used_today_at_snapshot``
    is used as the primary value, the missing day is correctly attributed 0
    and the next day gets its own per-day count from the API.

    Returns a list of exactly 4 ``AttackCount`` values.
    """
    ordered = sorted(snapshots, key=lambda s: s.snapshot_date)

    # Map each snapshot to its war-day index (0-3).
    day_map: dict[int, WarSnapshot] = {}
    for snap in ordered:
        offset = (snap.snapshot_date - war_start_date).days
        if 0 <= offset <= 3:
            day_map[offset] = snap

    result: list[AttackCount] = []
    prior: WarSnapshot | None = None
    for day_index in range(4):
        snap = day_map.get(day_index)
        if snap is None:
            # No snapshot for this day — 0 attacks, prior unchanged.
            result.append(AttackCount(0))
            continue

        # Prefer the API's own per-day count; fall back to the diff.
        diff = snap.attacks_since(prior)
        today = snap.decks_used_today_at_snapshot
        attacks = today if today > 0 else diff
        # Cap at 4 — physical maximum per war day.
        attacks = min(attacks, 4)
        result.append(AttackCount(attacks))
        prior = snap

    return result


@dataclass
class SnapshotRun:
    """Audit record for one execution of the snapshot collection script.

    Records the outcome (success / failure / no_war) so that missing
    snapshots can be detected and backfilled.
    """

    war_id: int | None
    clan_tag: str
    snapshot_date: date
    status: str  # "success", "failure", "no_war"
    participants_captured: int = 0
    error_message: str | None = None
    triggered_by: str = "cron"  # "cron" or "manual"
    captured_at: datetime | None = None
