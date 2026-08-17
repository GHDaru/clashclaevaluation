"""Secondary Port — Clash Royale API client interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from domain.model.value_objects import ClanTag, PlayerTag


@dataclass
class ClanInfo:
    tag: str
    name: str
    member_count: int


@dataclass
class PlayerInfo:
    tag: str
    name: str
    role: str
    exp_level: int


@dataclass
class WarParticipant:
    tag: str
    name: str
    fame: int
    decks_used: int
    decks_used_today: int


@dataclass
class ClanStanding:
    tag: str
    name: str
    fame: int
    clan_score: int


@dataclass
class CurrentWarData:
    state: str  # "active", "ended", None (no war)
    period_index: int  # 0-3
    period_type: str
    clan_score: int
    clan_fame: int  # today's fame
    participants: list[WarParticipant]
    period_points: list[int]
    clans: list[ClanStanding]  # all competing clans for placement


@dataclass
class BattleLogEntry:
    battle_date: str
    battle_type: str
    game_mode: str


@dataclass
class BattleLog:
    entries: list[BattleLogEntry]


class CRApiClient(ABC):
    """Interface for Clash Royale API. Infrastructure provides HTTP implementation."""

    @abstractmethod
    async def get_clan(self, tag: ClanTag) -> ClanInfo: ...

    @abstractmethod
    async def get_current_war(self, tag: ClanTag) -> CurrentWarData | None: ...

    @abstractmethod
    async def get_battle_log(self, tag: PlayerTag) -> BattleLog: ...

    @abstractmethod
    async def get_player(self, tag: PlayerTag) -> PlayerInfo: ...
