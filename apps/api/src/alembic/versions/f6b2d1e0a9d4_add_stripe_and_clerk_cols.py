"""add_stripe_and_clerk_cols

Revision ID: f6b2d1e0a9d4
Revises: a60410aac577
Create Date: 2026-03-28 06:45:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'f6b2d1e0a9d4'
down_revision: Union[str, Sequence[str], None] = 'a60410aac577'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Use batch_alter_table for broader compatibility
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('stripe_customer_id', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('clerk_id', sa.String(), nullable=True))
        batch_op.create_index(batch_op.f('ix_users_stripe_customer_id'), ['stripe_customer_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_users_clerk_id'), ['clerk_id'], unique=True)

def downgrade() -> None:
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_users_clerk_id'))
        batch_op.drop_index(batch_op.f('ix_users_stripe_customer_id'))
        batch_op.drop_column('clerk_id')
        batch_op.drop_column('stripe_customer_id')
