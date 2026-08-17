"""Infrastructure configuration — loads from environment / .env."""

from pathlib import Path

from pydantic import field_validator
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

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, v: str | None) -> str | None:
        """Normalize DATABASE_URL for SQLAlchemy async + asyncpg.

        Two transformations:
        1. ``postgresql://`` → ``postgresql+asyncpg://`` (async driver)
        2. ``sslmode=...`` → ``ssl=...`` (asyncpg uses ``ssl``, not ``sslmode``)

        Cloud providers (Neon, Railway, Render) provision DATABASE_URL as
        ``postgresql://user:pass@host/db?sslmode=require``. SQLAlchemy's
        async engine needs the asyncpg driver, and asyncpg's connect() does
        not accept the libpq ``sslmode`` keyword.
        """
        if not v:
            return v

        # 1. Switch to asyncpg driver
        if v.startswith("postgresql://"):
            v = v.replace("postgresql://", "postgresql+asyncpg://", 1)

        # 2. Convert sslmode → ssl for asyncpg compatibility
        if "sslmode=" in v:
            v = v.replace("sslmode=", "ssl=")

        return v


settings = Settings()
