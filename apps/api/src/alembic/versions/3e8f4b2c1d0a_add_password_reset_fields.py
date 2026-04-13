"""add_password_reset_fields

Revision ID: 3e8f4b2c1d0a
Revises: f6b2d1e0a9d4
Create Date: 2026-03-28 07:12:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '3e8f4b2c1d0a'
down_revision: Union[str, Sequence[str], None] = 'f6b2d1e0a9d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Adding columns for password reset functionality
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('password_reset_token', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('password_reset_expires', sa.DateTime(timezone=True), nullable=True))
        batch_op.create_index(batch_op.f('ix_users_password_reset_token'), ['password_reset_token'], unique=False)

def downgrade() -> None:
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_users_password_reset_token'))
        batch_op.drop_column('password_reset_expires')
        batch_op.drop_column('password_reset_token')
