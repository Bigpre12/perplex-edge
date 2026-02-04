"""Add users table for authentication and subscriptions.

Revision ID: 20260204_000000
Revises: 20260203_000000
Create Date: 2026-02-04 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260204_000000'
down_revision = '20260203_000000'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(255), primary_key=True),  # Clerk user ID
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('first_name', sa.String(100), nullable=True),
        sa.Column('last_name', sa.String(100), nullable=True),
        sa.Column('plan', sa.String(20), nullable=False, server_default='free'),
        sa.Column('trial_ends_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('whop_membership_id', sa.String(255), nullable=True),
        sa.Column('props_viewed_today', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('props_reset_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )
    
    # Create indexes
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_whop_membership', 'users', ['whop_membership_id'])
    op.create_index('ix_users_plan', 'users', ['plan'])


def downgrade() -> None:
    op.drop_index('ix_users_plan', table_name='users')
    op.drop_index('ix_users_whop_membership', table_name='users')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')
