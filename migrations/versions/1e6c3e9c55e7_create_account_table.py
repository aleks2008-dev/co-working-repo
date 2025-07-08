"""create account table

Revision ID: 1e6c3e9c55e7
Revises: 201bf2bfc759
Create Date: 2025-01-21 19:20:51.453486

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel             # NEW


# revision identifiers, used by Alembic.
revision = '1e6c3e9c55e7'
down_revision = '201bf2bfc759'
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass