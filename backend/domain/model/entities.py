"""Domain Entities — objects with continuous identity."""

from dataclasses import dataclass
from datetime import datetime

from domain.model.value_objects import ClanTag, PlayerTag


@dataclass
class Player:
    """A Clash Royale player. Identified by PlayerTag (immutable in CR)."""

    tag: PlayerTag
    name: str
    role: str  # "leader", "coLeader", "elder", "member"
    first_seen: datetime
    last_seen: datetime

    def update_name(self, new_name: str) -> None:
        self.name = new_name

    def update_role(self, new_role: str) -> None:
        allowed = {"leader", "coLeader", "elder", "member"}
        if new_role not in allowed:
            raise ValueError(f"Invalid role: {new_role}. Allowed: {allowed}")
        self.role = new_role

    def mark_seen(self, when: datetime) -> None:
        self.last_seen = when


@dataclass
class Clan:
    """A Clash Royale clan. Identified by ClanTag (immutable in CR)."""

    tag: ClanTag
    name: str
    created_at: datetime
    updated_at: datetime

    def update_name(self, new_name: str) -> None:
        self.name = new_name
