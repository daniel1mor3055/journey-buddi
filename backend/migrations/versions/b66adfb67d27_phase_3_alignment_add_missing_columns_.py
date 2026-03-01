"""phase_3_alignment_add_missing_columns_and_tables

Revision ID: b66adfb67d27
Revises: d3e967e5838a
Create Date: 2026-03-01 16:40:43.320002

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'b66adfb67d27'
down_revision: Union[str, None] = 'd3e967e5838a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('condition_records',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('location_lat', sa.Float(), nullable=False),
        sa.Column('location_lon', sa.Float(), nullable=False),
        sa.Column('recorded_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('forecast_for', sa.DateTime(timezone=True), nullable=True),
        sa.Column('source', sa.String(length=50), nullable=False),
        sa.Column('data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('push_subscriptions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('endpoint', sa.Text(), nullable=False),
        sa.Column('p256dh_key', sa.Text(), nullable=False),
        sa.Column('auth_key', sa.Text(), nullable=False),
        sa.Column('user_agent', sa.String(length=500), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_push_subscriptions_user_id'), 'push_subscriptions', ['user_id'], unique=False)

    op.add_column('conversations', sa.Column('conversation_type', sa.String(length=20), server_default='planning', nullable=False))

    op.add_column('daily_briefings', sa.Column('day_id', sa.UUID(), nullable=True))
    op.add_column('daily_briefings', sa.Column('conditions_snapshot', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('daily_briefings', sa.Column('delivered_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('daily_briefings', sa.Column('viewed_at', sa.DateTime(timezone=True), nullable=True))
    op.create_foreign_key('fk_daily_briefings_day_id', 'daily_briefings', 'itinerary_days', ['day_id'], ['id'])

    op.add_column('itinerary_activities', sa.Column('duration_hours', sa.Float(), nullable=True))
    op.add_column('itinerary_activities', sa.Column('time_of_day', sa.String(length=20), nullable=True))
    op.add_column('itinerary_activities', sa.Column('suggested_start', sa.String(length=10), nullable=True))
    op.add_column('itinerary_activities', sa.Column('weather_sensitivity', sa.String(length=20), nullable=True))
    op.add_column('itinerary_activities', sa.Column('conditions_needed', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('itinerary_activities', sa.Column('packing_notes', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('itinerary_activities', sa.Column('pro_tips', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('itinerary_activities', sa.Column('swap_priority', sa.Integer(), nullable=True))
    op.add_column('itinerary_activities', sa.Column('status', sa.String(length=20), server_default='planned', nullable=False))

    op.add_column('itinerary_days', sa.Column('day_type', sa.String(length=20), nullable=True))
    op.add_column('itinerary_days', sa.Column('tightness_score', sa.Float(), nullable=True))
    op.add_column('itinerary_days', sa.Column('accommodation_zone', sa.String(length=255), nullable=True))
    op.add_column('itinerary_days', sa.Column('condition_forecast', postgresql.JSONB(astext_type=sa.Text()), nullable=True))

    op.add_column('swap_suggestions', sa.Column('original_day_id', sa.UUID(), nullable=True))
    op.add_column('swap_suggestions', sa.Column('swap_day_id', sa.UUID(), nullable=True))
    op.create_foreign_key('fk_swap_suggestions_original_day', 'swap_suggestions', 'itinerary_days', ['original_day_id'], ['id'])
    op.create_foreign_key('fk_swap_suggestions_swap_day', 'swap_suggestions', 'itinerary_days', ['swap_day_id'], ['id'])


def downgrade() -> None:
    op.drop_constraint('fk_swap_suggestions_swap_day', 'swap_suggestions', type_='foreignkey')
    op.drop_constraint('fk_swap_suggestions_original_day', 'swap_suggestions', type_='foreignkey')
    op.drop_column('swap_suggestions', 'swap_day_id')
    op.drop_column('swap_suggestions', 'original_day_id')
    op.drop_column('itinerary_days', 'condition_forecast')
    op.drop_column('itinerary_days', 'accommodation_zone')
    op.drop_column('itinerary_days', 'tightness_score')
    op.drop_column('itinerary_days', 'day_type')
    op.drop_column('itinerary_activities', 'status')
    op.drop_column('itinerary_activities', 'swap_priority')
    op.drop_column('itinerary_activities', 'pro_tips')
    op.drop_column('itinerary_activities', 'packing_notes')
    op.drop_column('itinerary_activities', 'conditions_needed')
    op.drop_column('itinerary_activities', 'weather_sensitivity')
    op.drop_column('itinerary_activities', 'suggested_start')
    op.drop_column('itinerary_activities', 'time_of_day')
    op.drop_column('itinerary_activities', 'duration_hours')
    op.drop_constraint('fk_daily_briefings_day_id', 'daily_briefings', type_='foreignkey')
    op.drop_column('daily_briefings', 'viewed_at')
    op.drop_column('daily_briefings', 'delivered_at')
    op.drop_column('daily_briefings', 'conditions_snapshot')
    op.drop_column('daily_briefings', 'day_id')
    op.drop_column('conversations', 'conversation_type')
    op.drop_index(op.f('ix_push_subscriptions_user_id'), table_name='push_subscriptions')
    op.drop_table('push_subscriptions')
    op.drop_table('condition_records')
