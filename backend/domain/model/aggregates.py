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
