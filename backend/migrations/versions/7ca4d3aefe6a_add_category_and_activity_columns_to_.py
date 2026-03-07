"""add category and activity columns to attractions

Revision ID: 7ca4d3aefe6a
Revises: b66adfb67d27
Create Date: 2026-03-07 15:37:50.584321

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '7ca4d3aefe6a'
down_revision: Union[str, None] = 'b66adfb67d27'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('attractions', sa.Column('category', sa.String(length=50), nullable=True))
    op.add_column('attractions', sa.Column('activity', sa.String(length=100), nullable=True))
    op.create_index(op.f('ix_attractions_activity'), 'attractions', ['activity'], unique=False)
    op.create_index(op.f('ix_attractions_category'), 'attractions', ['category'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_attractions_category'), table_name='attractions')
    op.drop_index(op.f('ix_attractions_activity'), table_name='attractions')
    op.drop_column('attractions', 'activity')
    op.drop_column('attractions', 'category')
