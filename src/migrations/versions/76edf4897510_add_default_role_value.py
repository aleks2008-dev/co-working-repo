"""add_default_role_value

Revision ID: 76edf4897510
Revises: bdd18581efea
Create Date: 2025-06-19 16:34:22.346537

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '76edf4897510'
down_revision: Union[str, None] = 'bdd18581efea'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # 1. Создаем временный тип для обхода ошибки
    op.execute("CREATE TYPE userrole_temp AS ENUM ('user', 'admin')")

    # 2. Конвертируем существующие данные
    op.execute("""
    ALTER TABLE users 
    ALTER COLUMN role TYPE userrole_temp 
    USING role::text::userrole_temp
    """)

    # 3. Удаляем старый тип и переименовываем новый
    op.execute("DROP TYPE IF EXISTS userrole")
    op.execute("ALTER TYPE userrole_temp RENAME TO userrole")

    # 4. Устанавливаем DEFAULT значение
    op.alter_column('users', 'role',
                    server_default='user',
                    nullable=False)


def downgrade():
    op.alter_column('users', 'role',
                    server_default=None,
                    nullable=True)
