"""Add Phase 2 models

Revision ID: ea982cd4a3f5
Revises: 0bdfca592133
Create Date: 2026-02-27 00:24:11.161062

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'ea982cd4a3f5'
down_revision: Union[str, None] = '0bdfca592133'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('attractions',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('destination', sa.String(length=100), nullable=False),
    sa.Column('region', sa.String(length=100), nullable=True),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('slug', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('types', postgresql.ARRAY(sa.String()), nullable=False),
    sa.Column('location_name', sa.String(length=255), nullable=True),
    sa.Column('latitude', sa.Float(), nullable=True),
    sa.Column('longitude', sa.Float(), nullable=True),
    sa.Column('difficulty', sa.String(length=20), nullable=True),
    sa.Column('cost_level', sa.String(length=20), nullable=True),
    sa.Column('duration_min', sa.Float(), nullable=True),
    sa.Column('duration_max', sa.Float(), nullable=True),
    sa.Column('seasonal_availability', sa.String(length=100), nullable=False),
    sa.Column('booking_required', sa.Boolean(), nullable=False),
    sa.Column('weather_sensitivity', sa.String(length=20), nullable=False),
    sa.Column('ideal_conditions', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('acceptable_conditions', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('dealbreaker_conditions', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('logistics', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('pro_tips', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('uniqueness_score', sa.Integer(), nullable=False),
    sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_attractions_destination'), 'attractions', ['destination'], unique=False)
    op.create_index(op.f('ix_attractions_slug'), 'attractions', ['slug'], unique=True)

    op.create_table('conversations',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('trip_id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=True),
    sa.Column('planning_step', sa.String(length=50), nullable=False),
    sa.Column('planning_state', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['trip_id'], ['trips.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_conversations_trip_id'), 'conversations', ['trip_id'], unique=False)
    op.create_index(op.f('ix_conversations_user_id'), 'conversations', ['user_id'], unique=False)

    op.create_table('itinerary_days',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('trip_id', sa.UUID(), nullable=False),
    sa.Column('day_number', sa.Integer(), nullable=False),
    sa.Column('date', sa.Date(), nullable=True),
    sa.Column('location', sa.String(length=255), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=True),
    sa.Column('summary', sa.Text(), nullable=True),
    sa.Column('is_flex_day', sa.Boolean(), nullable=False),
    sa.Column('is_arrival', sa.Boolean(), nullable=False),
    sa.Column('is_departure', sa.Boolean(), nullable=False),
    sa.Column('is_locked', sa.Boolean(), nullable=False),
    sa.Column('accommodation', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('transport', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('weather', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['trip_id'], ['trips.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_itinerary_days_trip_id'), 'itinerary_days', ['trip_id'], unique=False)

    op.create_table('trip_attractions',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('trip_id', sa.UUID(), nullable=False),
    sa.Column('attraction_id', sa.UUID(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('selected_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['attraction_id'], ['attractions.id'], ),
    sa.ForeignKeyConstraint(['trip_id'], ['trips.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_trip_attractions_attraction_id'), 'trip_attractions', ['attraction_id'], unique=False)
    op.create_index(op.f('ix_trip_attractions_trip_id'), 'trip_attractions', ['trip_id'], unique=False)

    op.create_table('itinerary_activities',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('itinerary_day_id', sa.UUID(), nullable=False),
    sa.Column('attraction_id', sa.UUID(), nullable=True),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('emoji', sa.String(length=10), nullable=False),
    sa.Column('provider', sa.String(length=255), nullable=True),
    sa.Column('time_start', sa.String(length=10), nullable=True),
    sa.Column('time_end', sa.String(length=10), nullable=True),
    sa.Column('price', sa.Float(), nullable=False),
    sa.Column('currency', sa.String(length=10), nullable=False),
    sa.Column('booking_status', sa.String(length=20), nullable=False),
    sa.Column('booking_ref', sa.String(length=100), nullable=True),
    sa.Column('condition_score', sa.Integer(), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('sort_order', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['attraction_id'], ['attractions.id'], ),
    sa.ForeignKeyConstraint(['itinerary_day_id'], ['itinerary_days.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_itinerary_activities_itinerary_day_id'), 'itinerary_activities', ['itinerary_day_id'], unique=False)

    op.create_table('messages',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('conversation_id', sa.UUID(), nullable=False),
    sa.Column('role', sa.String(length=20), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('message_type', sa.String(length=30), nullable=False),
    sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('sort_order', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_messages_conversation_id'), 'messages', ['conversation_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_messages_conversation_id'), table_name='messages')
    op.drop_table('messages')
    op.drop_index(op.f('ix_itinerary_activities_itinerary_day_id'), table_name='itinerary_activities')
    op.drop_table('itinerary_activities')
    op.drop_index(op.f('ix_trip_attractions_trip_id'), table_name='trip_attractions')
    op.drop_index(op.f('ix_trip_attractions_attraction_id'), table_name='trip_attractions')
    op.drop_table('trip_attractions')
    op.drop_index(op.f('ix_itinerary_days_trip_id'), table_name='itinerary_days')
    op.drop_table('itinerary_days')
    op.drop_index(op.f('ix_conversations_user_id'), table_name='conversations')
    op.drop_index(op.f('ix_conversations_trip_id'), table_name='conversations')
    op.drop_table('conversations')
    op.drop_index(op.f('ix_attractions_slug'), table_name='attractions')
    op.drop_index(op.f('ix_attractions_destination'), table_name='attractions')
    op.drop_table('attractions')
