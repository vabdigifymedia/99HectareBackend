"""add_inquiry_admin_approval

Revision ID: 8dc675c5c0e8
Revises: e664ed92cdab
Create Date: 2026-09-17 23:56:49.606667
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '8dc675c5c0e8'
down_revision: Union[str, None] = 'e664ed92cdab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'inquiries',
        sa.Column('is_admin_approved', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    )
    op.add_column(
        'inquiries',
        sa.Column('admin_notes', sa.Text(), nullable=True),
    )
    op.create_index(op.f('ix_inquiries_is_admin_approved'), 'inquiries', ['is_admin_approved'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_inquiries_is_admin_approved'), table_name='inquiries')
    op.drop_column('inquiries', 'admin_notes')
    op.drop_column('inquiries', 'is_admin_approved')

