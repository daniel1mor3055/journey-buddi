"""add_phase_3_models

Revision ID: d3e967e5838a
Revises: ea982cd4a3f5
Create Date: 2026-02-27 23:37:34.582947

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd3e967e5838a'
down_revision: Union[str, None] = 'ea982cd4a3f5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('daily_briefings',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('trip_id', sa.UUID(), nullable=False),
    sa.Column('day_number', sa.Integer(), nullable=False),
    sa.Column('briefing_date', sa.Date(), nullable=False),
    sa.Column('location', sa.String(length=255), nullable=False),
    sa.Column('overall_score', sa.Integer(), nullable=False),
    sa.Column('overall_assessment', sa.String(length=20), nullable=False),
    sa.Column('confidence', sa.String(length=20), nullable=False),
    sa.Column('weather_summary', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('solar_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('activity_reports', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('packing_list', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('timeline', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('hidden_gem', sa.Text(), nullable=True),
    sa.Column('lookahead', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('ai_narrative', sa.Text(), nullable=True),
    sa.Column('swap_suggestion', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['trip_id'], ['trips.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_daily_briefings_trip_id'), 'daily_briefings', ['trip_id'], unique=False)
    op.create_table('swap_suggestions',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('trip_id', sa.UUID(), nullable=False),
    sa.Column('original_day', sa.Integer(), nullable=False),
    sa.Column('suggested_day', sa.Integer(), nullable=False),
    sa.Column('reason', sa.Text(), nullable=False),
    sa.Column('improvement_score', sa.Integer(), nullable=False),
    sa.Column('disruption_score', sa.Integer(), nullable=False),
    sa.Column('recommendation', sa.String(length=30), nullable=False),
    sa.Column('original_conditions', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('suggested_conditions', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('details', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['trip_id'], ['trips.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_swap_suggestions_trip_id'), 'swap_suggestions', ['trip_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_swap_suggestions_trip_id'), table_name='swap_suggestions')
    op.drop_table('swap_suggestions')
    op.drop_index(op.f('ix_daily_briefings_trip_id'), table_name='daily_briefings')
    op.drop_table('daily_briefings')
