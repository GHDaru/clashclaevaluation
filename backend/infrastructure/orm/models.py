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


class WarSnapshotModel(Base):
    """Daily snapshot of a participant's cumulative war progress.

    The Clash Royale API (/clans/{tag}/currentriverrace) only exposes
    cumulative counters (decksUsed, decksUsedToday, fame) with no per-day
    breakdown. By capturing one snapshot per war-day and diffing consecutive
    snapshots, per-day attack counts can be reconstructed:

        attacks_on_day_X = decks_used_at_snapshot(day_X)
                          - decks_used_at_snapshot(day_X-1)

    Idempotency is enforced by the unique constraint on
    (war_id, player_tag, snapshot_date) — re-capturing a snapshot for the
    same war/player/date performs an upsert, not a duplicate insert.
    """

    __tablename__ = "war_snapshots"
    __table_args__ = (
        UniqueConstraint(
            "war_id",
            "player_tag",
            "snapshot_date",
            name="uq_warsnapshot_war_player_date",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    war_id: Mapped[int] = mapped_column(Integer, ForeignKey("wars.id"))
    player_tag: Mapped[str] = mapped_column(String(12), ForeignKey("players.tag"))
    player_name: Mapped[str] = mapped_column(String(100))
    snapshot_date: Mapped[date] = mapped_column(Date)
    # Cumulative decksUsed from API at snapshot time (0-16 over the full war)
    decks_used_at_snapshot: Mapped[int] = mapped_column(Integer, default=0)
    # decksUsedToday from API at snapshot time (0-4) — cross-check for the diff
    decks_used_today_at_snapshot: Mapped[int] = mapped_column(Integer, default=0)
    # Cumulative fame from API at snapshot time
    fame_at_snapshot: Mapped[int] = mapped_column(Integer, default=0)
    captured_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class SnapshotRunModel(Base):
    """Audit log for snapshot collection runs.

    Each execution of the snapshot script (cron or manual) records one row
    with the outcome: success, failure, or no_war. This enables completeness
    checking — detecting war days where no snapshot was captured.
    """

    __tablename__ = "snapshot_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    war_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("wars.id"))
    clan_tag: Mapped[str] = mapped_column(String(12))
    snapshot_date: Mapped[date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(20))  # success, failure, no_war
    participants_captured: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(String(500))
    triggered_by: Mapped[str] = mapped_column(String(20), default="cron")  # cron, manual
    captured_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class EvaluationLogModel(Base):
    __tablename__ = "evaluation_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    war_id: Mapped[int] = mapped_column(Integer, ForeignKey("wars.id"))
    evaluated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    triggered_by: Mapped[str] = mapped_column(String(20))
    config_snapshot: Mapped[dict] = mapped_column(JSON)
