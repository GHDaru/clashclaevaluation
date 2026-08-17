"""Infrastructure configuration — loads from environment / .env."""

from pathlib import Path

from pydantic_settings import BaseSettings

# Always resolve .env relative to this file (backend/infrastructure/ → backend/.env)
_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    # Clash Royale API
    cr_api_key: str = ""
    cr_api_base_url: str = "https://api.clashroyale.com/v1"
    cr_clan_tag: str = ""  # e.g. "#ABC123"

    # Database
    database_url: str = "sqlite+aiosqlite:///clashclan.db"

    # Evaluation defaults
    attacks_per_day: int = 4
    yellow_to_red: int = 4
    red_to_black: int = 4
    min_points_warning: int = 1600
    min_points_critical: int = 0
    relax_on_first_place: bool = True
    recency_weeks: int = 4
    history_months: int = 3

    model_config = {"env_file": str(_ENV_PATH), "env_file_encoding": "utf-8"}


settings = Settings()
