"""add snapshot_runs audit table

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-08-17 00:00:01.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = 'b2c3d4e5f6a7'
down_revision: str | None = 'a1b2c3d4e5f6'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'snapshot_runs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('war_id', sa.Integer(), nullable=True),
        sa.Column('clan_tag', sa.String(length=12), nullable=False),
        sa.Column('snapshot_date', sa.Date(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('participants_captured', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('error_message', sa.String(length=500), nullable=True),
        sa.Column('triggered_by', sa.String(length=20), nullable=False, server_default='cron'),
        sa.Column('captured_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['war_id'], ['wars.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        'ix_snapshot_runs_date',
        'snapshot_runs',
        ['snapshot_date'],
    )


def downgrade() -> None:
    op.drop_index('ix_snapshot_runs_date', table_name='snapshot_runs')
    op.drop_table('snapshot_runs')
