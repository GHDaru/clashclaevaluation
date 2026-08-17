"""Domain Events — something that happened in the domain."""

from dataclasses import dataclass
from datetime import datetime

from domain.model.value_objects import PlayerTag


@dataclass
class BlackCardIssued:
    """A BlackCard was issued to a player — candidate for expulsion."""

    player_tag: PlayerTag
    player_name: str
    war_id: int
    total_black: int
    reason: str
    occurred_at: datetime


@dataclass
class EarlyVictoryDetected:
    """The clan achieved EarlyVictory — remaining WarDays are relaxed."""

    clan_tag: str
    war_id: int
    victory_day_index: int  # 0-3, the day victory was achieved
    relaxed_days: list[int]  # remaining days
    occurred_at: datetime


@dataclass
class EvaluationCompleted:
    """An Evaluation of a War was completed."""

    war_id: int
    players_evaluated: int
    clean: int
    warnings: int
    danger: int
    critical: int
    occurred_at: datetime
