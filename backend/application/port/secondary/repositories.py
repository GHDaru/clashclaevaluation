"""Secondary Ports — interfaces the domain needs from infrastructure.

These are ABSTRACT (protocols/ABCs). Infrastructure provides concrete implementations.
Domain and Application depend on these interfaces, never on implementations.
"""

from abc import ABC, abstractmethod
from datetime import date

from domain.model.aggregates import PlayerWar, War, WarSnapshot
from domain.model.entities import Clan, Player
from domain.model.value_objects import ClanTag, PlayerTag


class WarRepository(ABC):
    """Repository for War aggregate."""

    @abstractmethod
    async def get_by_id(self, war_id: int) -> War | None: ...

    @abstractmethod
    async def get_by_clan_and_date(
        self, clan_tag: ClanTag, start_date: date
    ) -> War | None: ...

    @abstractmethod
    async def get_recent(self, clan_tag: ClanTag, limit: int = 12) -> list[War]: ...

    @abstractmethod
    async def save(self, war: War) -> War: ...


class PlayerRepository(ABC):
    """Repository for Player entity."""

    @abstractmethod
    async def get_by_tag(self, tag: PlayerTag) -> Player | None: ...

    @abstractmethod
    async def save(self, player: Player) -> Player: ...

    @abstractmethod
    async def get_by_clan(self, clan_tag: ClanTag) -> list[Player]: ...


class PlayerWarRepository(ABC):
    """Repository for PlayerWar (part of War aggregate)."""

    @abstractmethod
    async def get_by_war(self, war_id: int) -> list[PlayerWar]: ...

    @abstractmethod
    async def get_by_player(
        self, tag: PlayerTag, limit: int = 12
    ) -> list[PlayerWar]: ...


class ClanRepository(ABC):
    """Repository for Clan entity."""

    @abstractmethod
    async def get_by_tag(self, tag: ClanTag) -> Clan | None: ...

    @abstractmethod
    async def save(self, clan: Clan) -> Clan: ...


class WarSnapshotRepository(ABC):
    """Repository for WarSnapshot — daily war progress captures."""

    @abstractmethod
    async def get_by_war(
        self, war_id: int
    ) -> list[WarSnapshot]:
        """Return all snapshots for a war, across all players and days."""
        ...

    @abstractmethod
    async def get_by_war_and_player(
        self, war_id: int, player_tag: PlayerTag
    ) -> list[WarSnapshot]:
        """Return all snapshots for one player in a war, ordered by date."""
        ...

    @abstractmethod
    async def save(self, snapshot: WarSnapshot) -> WarSnapshot:
        """Upsert a snapshot (idempotent on war_id + player_tag + snapshot_date)."""
        ...
