"""Domain Model public interface — re-exports all domain objects."""

from domain.model.aggregates import (
    PlayerStatus,
    PlayerWar,
    Trend,
    War,
    WarStatus,
)
from domain.model.entities import Clan, Player
from domain.model.value_objects import (
    AttackCount,
    BlackCard,
    CardSummary,
    ClanTag,
    PeriodPoints,
    PlayerTag,
    RedCard,
    WarDay,
    YellowCard,
)

__all__ = [
    # Value Objects
    "PlayerTag",
    "ClanTag",
    "AttackCount",
    "YellowCard",
    "RedCard",
    "BlackCard",
    "CardSummary",
    "WarDay",
    "PeriodPoints",
    # Entities
    "Player",
    "Clan",
    # Aggregates
    "War",
    "PlayerWar",
    "WarStatus",
    "PlayerStatus",
    "Trend",
]
