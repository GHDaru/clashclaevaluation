"""SQLAlchemy ORM models — mirror domain entities for persistence."""

from datetime import date, datetime

from sqlalchemy import JSON, Boolean, Date, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ClanModel(Base):
    __tablename__ = "clans"

    tag: Mapped[str] = mapped_column(String(12), primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class PlayerModel(Base):
    __tablename__ = "players"

    tag: Mapped[str] = mapped_column(String(12), primary_key=True)
    clan_tag: Mapped[str | None] = mapped_column(String(12), ForeignKey("clans.tag"))
    name: Mapped[str] = mapped_column(String(100))
    role: Mapped[str] = mapped_column(String(20))
    first_seen: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_seen: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class WarModel(Base):
    __tablename__ = "wars"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    clan_tag: Mapped[str] = mapped_column(String(12), ForeignKey("clans.tag"))
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(20))
    total_fame: Mapped[int] = mapped_column(Integer, default=0)
    relaxed_days: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class PlayerWarModel(Base):
    __tablename__ = "player_wars"
    __table_args__ = (
        UniqueConstraint("war_id", "player_tag", name="uq_playerwar_war_player"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    war_id: Mapped[int] = mapped_column(Integer, ForeignKey("wars.id"))
    player_tag: Mapped[str] = mapped_column(String(12), ForeignKey("players.tag"))
    player_name: Mapped[str] = mapped_column(String(100))
    attacks_day1: Mapped[int] = mapped_column(Integer, default=0)
    attacks_day2: Mapped[int] = mapped_column(Integer, default=0)
    attacks_day3: Mapped[int] = mapped_column(Integer, default=0)
    attacks_day4: Mapped[int] = mapped_column(Integer, default=0)
    total_points: Mapped[int] = mapped_column(Integer, default=0)
    yellow_cards: Mapped[int] = mapped_column(Integer, default=0)
    red_cards: Mapped[int] = mapped_column(Integer, default=0)
    black_cards: Mapped[int] = mapped_column(Integer, default=0)
    incomplete: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class EvaluationLogModel(Base):
    __tablename__ = "evaluation_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    war_id: Mapped[int] = mapped_column(Integer, ForeignKey("wars.id"))
    evaluated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    triggered_by: Mapped[str] = mapped_column(String(20))
    config_snapshot: Mapped[dict] = mapped_column(JSON)
