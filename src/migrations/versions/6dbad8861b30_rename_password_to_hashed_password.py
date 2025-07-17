"""Rename password to hashed_password

Revision ID: 6dbad8861b30
Revises: f3d6f88fea3a
Create Date: 2025-07-17 04:54:12.252429

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '6dbad8861b30'
down_revision: Union[str, None] = 'f3d6f88fea3a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade():
    # 1. Сначала добавляем новую колонку
    op.add_column('users', sa.Column('hashed_password', sa.String(), nullable=True))

    # 2. Копируем данные из старой колонки в новую
    op.execute('UPDATE users SET hashed_password = password')

    # 3. Удаляем старую колонку
    op.drop_column('users', 'password')

    # 4. Делаем новую колонку NOT NULL (если нужно)
    op.alter_column('users', 'hashed_password', nullable=False)


def downgrade():
    # 1. Добавляем обратно старую колонку
    op.add_column('users', sa.Column('password', sa.String(), nullable=True))

    # 2. Копируем данные обратно
    op.execute('UPDATE users SET password = hashed_password')

    # 3. Удаляем новую колонку
    op.drop_column('users', 'hashed_password')

    # 4. Возвращаем NOT NULL (если было)
    op.alter_column('users', 'password', nullable=False)