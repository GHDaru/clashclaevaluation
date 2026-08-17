"""add war_snapshots table

Revision ID: a1b2c3d4e5f6
Revises: dfcf5ad77d2e
Create Date: 2026-08-17 00:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = 'a1b2c3d4e5f6'
down_revision: str | None = 'dfcf5ad77d2e'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'war_snapshots',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('war_id', sa.Integer(), nullable=False),
        sa.Column('player_tag', sa.String(length=12), nullable=False),
        sa.Column('player_name', sa.String(length=100), nullable=False),
        sa.Column('snapshot_date', sa.Date(), nullable=False),
        sa.Column('decks_used_at_snapshot', sa.Integer(), nullable=False),
        sa.Column('decks_used_today_at_snapshot', sa.Integer(), nullable=False),
        sa.Column('fame_at_snapshot', sa.Integer(), nullable=False),
        sa.Column('captured_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['war_id'], ['wars.id'], ),
        sa.ForeignKeyConstraint(['player_tag'], ['players.tag'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint(
            'war_id', 'player_tag', 'snapshot_date',
            name='uq_warsnapshot_war_player_date',
        ),
    )
    # Index for the common query: all snapshots for a war, ordered by player+date
    op.create_index(
        'ix_warsnapshot_war_date',
        'war_snapshots',
        ['war_id', 'snapshot_date'],
    )


def downgrade() -> None:
    op.drop_index('ix_warsnapshot_war_date', table_name='war_snapshots')
    op.drop_table('war_snapshots')
