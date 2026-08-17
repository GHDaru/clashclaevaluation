"""FastAPI routes — Primary Adapter (HTTP REST).

All endpoints are wired to use cases via dependency injection.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from application.di import (
    get_clan_status_use_case,
    get_evaluate_use_case,
    get_player_history_use_case,
    get_settings,
)
from application.port.primary.use_cases import (
    EvaluateClanUseCase,
    EvaluateCommand,
    GetClanStatusUseCase,
    GetPlayerHistoryUseCase,
)
from domain.model.value_objects import ClanTag, PlayerTag
from infrastructure.config import Settings

router = APIRouter(prefix="/api/v1")


# --- Config request/response models ---


class ConfigUpdate(BaseModel):
    attacks_per_day: int | None = None
    yellow_to_red: int | None = None
    red_to_black: int | None = None
    min_points_warning: int | None = None
    min_points_critical: int | None = None
    relax_on_first_place: bool | None = None
    cr_clan_tag: str | None = None


# --- Endpoints ---


@router.get("/clan/status")
async def get_clan_status(
    clan_tag: str | None = None,
    use_case: GetClanStatusUseCase = Depends(get_clan_status_use_case),
    settings: Settings = Depends(get_settings),
):
    """GET /api/v1/clan/status — current War status for the whole clan.

    Accepts optional ?clan_tag= query param to override the configured clan.
    """
    effective_tag = clan_tag or settings.cr_clan_tag
    if not effective_tag:
        raise HTTPException(
            status_code=400,
            detail="Clan tag not provided. Pass ?clan_tag= or set CR_CLAN_TAG in config.",
        )
    try:
        clan_tag_obj = ClanTag(effective_tag if effective_tag.startswith("#") else f"#{effective_tag}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    result = await use_case.execute(clan_tag_obj)
    return {
        "war_active": result.war_active,
        "war_id": result.war_id,
        "day": result.day,
        "day_label": result.day_label,
        "status": result.status,
        "position": result.position,
        "total_fame": result.total_fame,
        "daily_fame": result.daily_fame,
        "clans_count": result.clans_count,
        "relaxed": result.relaxed,
        "players": [
            {
                "tag": p.tag,
                "name": p.name,
                "role": p.role,
                "attacks_today": p.attacks_today,
                "attacks_total": p.attacks_total,
                "total_points": p.total_points,
                "yellow_cards": p.yellow_cards,
                "red_cards": p.red_cards,
                "black_cards": p.black_cards,
                "status": p.status,
                "trend": p.trend,
                "in_clan": p.in_clan,
            }
            for p in result.players
        ],
    }


@router.get("/players/{player_tag}")
async def get_player_history(
    player_tag: str,
    expand: bool = False,
    use_case: GetPlayerHistoryUseCase = Depends(get_player_history_use_case),
):
    """GET /api/v1/players/{tag} — player detail and history."""
    try:
        tag = PlayerTag(f"#{player_tag.lstrip('#')}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    result = await use_case.execute(tag, expand=expand)
    return {
        "tag": result.tag,
        "name": result.name,
        "role": result.role,
        "first_seen": result.first_seen,
        "last_seen": result.last_seen,
        "current_war": result.current_war,
        "recency": result.recency,
        "history": result.history,
    }


@router.get("/wars")
async def list_wars(limit: int = 12):
    """GET /api/v1/wars — list past wars."""
    from application.di import get_war_repo
    from domain.model.value_objects import ClanTag
    from infrastructure.config import settings

    if not settings.cr_clan_tag:
        return {"wars": [], "limit": limit}

    war_repo = get_war_repo()
    wars = await war_repo.get_recent(ClanTag(settings.cr_clan_tag), limit=limit)
    return {
        "wars": [
            {
                "id": w.id,
                "start_date": w.start_date.isoformat(),
                "end_date": w.end_date.isoformat(),
                "status": w.status.value,
                "total_fame": w.total_fame,
                "relaxed_days": w.relaxed_days,
            }
            for w in wars
        ],
        "limit": limit,
    }


@router.get("/wars/{war_id}")
async def get_war_detail(
    war_id: int,
):
    """GET /api/v1/wars/{id} — detail of one war."""
    from application.di import get_player_war_repo, get_war_repo

    war_repo = get_war_repo()
    war = await war_repo.get_by_id(war_id)
    if war is None:
        raise HTTPException(status_code=404, detail=f"War {war_id} not found")

    player_war_repo = get_player_war_repo()
    player_wars = await player_war_repo.get_by_war(war_id)

    return {
        "id": war.id,
        "clan_tag": war.clan_tag,
        "start_date": war.start_date.isoformat(),
        "end_date": war.end_date.isoformat(),
        "status": war.status.value,
        "total_fame": war.total_fame,
        "relaxed_days": war.relaxed_days,
        "players": [
            {
                "tag": str(pw.player_tag),
                "name": pw.player_name,
                "attacks": [a.value for a in pw.attacks],
                "total_points": pw.total_points,
                "yellow_cards": pw.yellow_cards.count,
                "red_cards": pw.red_cards.count,
                "black_cards": pw.black_cards.count,
                "status": pw.status.value,
            }
            for pw in player_wars
        ],
    }


@router.post("/evaluate")
async def trigger_evaluation(
    use_case: EvaluateClanUseCase = Depends(get_evaluate_use_case),
    settings: Settings = Depends(get_settings),
):
    """POST /api/v1/evaluate — trigger evaluation for current war."""
    if not settings.cr_clan_tag:
        raise HTTPException(status_code=400, detail="Clan tag not configured.")

    command = EvaluateCommand(clan_tag=settings.cr_clan_tag)
    result = await use_case.execute(command)
    return {
        "war_id": result.war_id,
        "evaluated_at": result.evaluated_at,
        "players_evaluated": result.players_evaluated,
        "summary": result.summary,
    }


@router.get("/config")
async def get_config(settings: Settings = Depends(get_settings)):
    """GET /api/v1/config — get current configuration."""
    return {
        "cr_clan_tag": settings.cr_clan_tag,
        "attacks_per_day": settings.attacks_per_day,
        "yellow_to_red": settings.yellow_to_red,
        "red_to_black": settings.red_to_black,
        "min_points_warning": settings.min_points_warning,
        "min_points_critical": settings.min_points_critical,
        "relax_on_first_place": settings.relax_on_first_place,
        "recency_weeks": settings.recency_weeks,
        "history_months": settings.history_months,
    }


@router.put("/config")
async def update_config(config: ConfigUpdate):
    """PUT /api/v1/config — update configuration.

    Updates are written to .env file and reloaded.
    """
    from pathlib import Path

    env_path = Path(".env")
    lines: list[str] = []
    if env_path.exists():
        lines = env_path.read_text(encoding="utf-8").splitlines()

    # Build a dict of existing entries
    env_dict: dict[str, str] = {}
    for line in lines:
        if "=" in line and not line.startswith("#"):
            key, _, val = line.partition("=")
            env_dict[key.strip()] = val.strip()

    # Apply updates
    updates = {
        "ATTACKS_PER_DAY": config.attacks_per_day,
        "YELLOW_TO_RED": config.yellow_to_red,
        "RED_TO_BLACK": config.red_to_black,
        "MIN_POINTS_WARNING": config.min_points_warning,
        "MIN_POINTS_CRITICAL": config.min_points_critical,
        "RELAX_ON_FIRST_PLACE": config.relax_on_first_place,
        "CR_CLAN_TAG": config.cr_clan_tag,
    }
    for key, val in updates.items():
        if val is not None:
            env_dict[key] = str(val)

    # Write back
    new_lines = [f"{k}={v}" for k, v in env_dict.items()]
    env_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")

    updated = {k: v for k, v in updates.items() if v is not None}
    return {"message": "Configuration updated", "updated": updated}


@router.post("/config/defaults")
async def restore_defaults():
    """POST /api/v1/config/defaults — restore default configuration."""
    from pathlib import Path

    env_path = Path(".env")
    defaults = [
        "ATTACKS_PER_DAY=4",
        "YELLOW_TO_RED=4",
        "RED_TO_BLACK=4",
        "MIN_POINTS_WARNING=1600",
        "MIN_POINTS_CRITICAL=0",
        "RELAX_ON_FIRST_PLACE=true",
        "RECENCY_WEEKS=4",
        "HISTORY_MONTHS=3",
    ]
    env_path.write_text("\n".join(defaults) + "\n", encoding="utf-8")

    return {"message": "Defaults restored"}
