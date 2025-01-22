"""create account table

Revision ID: 201bf2bfc759
Revises: 98dfcdd95fb1
Create Date: 2025-01-21 19:12:43.165504

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel             # NEW


# revision identifiers, used by Alembic.
revision = '201bf2bfc759'
down_revision = '98dfcdd95fb1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass