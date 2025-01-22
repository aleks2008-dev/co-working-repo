"""first migrations

Revision ID: 98dfcdd95fb1
Revises: 
Create Date: 2025-01-21 13:42:38.910340

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel             # NEW


# revision identifiers, used by Alembic.
revision = '98dfcdd95fb1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass