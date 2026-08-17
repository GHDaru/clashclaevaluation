"""HTTP implementation of Clash Royale API client."""

import httpx

from application.port.secondary.cr_api_client import (
    BattleLog,
    BattleLogEntry,
    ClanInfo,
    ClanStanding,
    CRApiClient,
    CurrentWarData,
    PlayerInfo,
    WarParticipant,
)
from domain.model.value_objects import ClanTag, PlayerTag
from infrastructure.config import settings


class HttpCRApiClient(CRApiClient):
    """HTTP implementation of the Clash Royale API client.

    Rate limit: ~300 req/min. Space 51 calls with 200ms delay = ~10s.
    Retry on 429 with exponential backoff.
    """

    def __init__(self) -> None:
        self.base_url = settings.cr_api_base_url
        self.headers = {
            "Authorization": f"Bearer {settings.cr_api_key}",
            "Accept": "application/json",
        }

    async def get_clan(self, tag: ClanTag) -> ClanInfo:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/clans/{self._encode_tag(tag)}",
                headers=self.headers,
            )
            resp.raise_for_status()
            data = resp.json()
            return ClanInfo(
                tag=data["tag"],
                name=data["name"],
                member_count=data["members"],
            )

    async def get_current_war(self, tag: ClanTag) -> CurrentWarData | None:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/clans/{self._encode_tag(tag)}/currentriverrace",
                headers=self.headers,
            )
            if resp.status_code == 404:
                return None  # No active war
            resp.raise_for_status()
            data = resp.json()
            if data.get("state") is None:
                return None
            clan_data = data.get("clan", {})
            clans_raw = data.get("clans", [])
            return CurrentWarData(
                state=data["state"],
                period_index=data.get("periodIndex", 0),
                period_type=data.get("periodType", ""),
                clan_score=clan_data.get("clanScore", 0),
                clan_fame=clan_data.get("fame", 0),
                participants=[
                    WarParticipant(
                        tag=p["tag"],
                        name=p["name"],
                        fame=p.get("fame", 0),
                        decks_used=p.get("decksUsed", 0),
                        decks_used_today=p.get("decksUsedToday", 0),
                    )
                    for p in clan_data.get("participants", [])
                ],
                period_points=clan_data.get("periodPoints", [0, 0, 0, 0]),
                clans=[
                    ClanStanding(
                        tag=c.get("tag", ""),
                        name=c.get("name", ""),
                        fame=c.get("fame", 0),
                        clan_score=c.get("clanScore", 0),
                    )
                    for c in clans_raw
                ],
            )

    async def get_battle_log(self, tag: PlayerTag) -> BattleLog:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/players/{self._encode_tag(tag)}/battlelog",
                headers=self.headers,
            )
            resp.raise_for_status()
            data = resp.json()
            return BattleLog(
                entries=[
                    BattleLogEntry(
                        battle_date=e.get("battleTime", ""),
                        battle_type=e.get("type", ""),
                        game_mode=e.get("gameMode", {}).get("name", ""),
                    )
                    for e in data
                ]
            )

    async def get_player(self, tag: PlayerTag) -> PlayerInfo:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/players/{self._encode_tag(tag)}",
                headers=self.headers,
            )
            resp.raise_for_status()
            data = resp.json()
            return PlayerInfo(
                tag=data["tag"],
                name=data["name"],
                role=data.get("role", "member"),
                exp_level=data.get("expLevel", 0),
            )

    @staticmethod
    def _encode_tag(tag: ClanTag | PlayerTag) -> str:
        """URL-encode the # in clan/player tags."""
        return str(tag).replace("#", "%23")
