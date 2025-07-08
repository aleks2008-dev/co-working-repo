"""drop clients table and create users table

Revision ID: bdd18581efea
Revises: ec1362c67e94
Create Date: 2025-04-11 07:39:36.538080

"""
import uuid
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bdd18581efea'
down_revision: Union[str, None] = 'ec1362c67e94'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Удаляем внешние ключи и зависимости от clients (если они есть)
    op.drop_constraint('appointments_client_id_fkey', 'appointments', type_='foreignkey')

    # Удаляем таблицу clients
    op.drop_table('clients')

    op.drop_column('appointments', 'client_id')

    # Создаем таблицу users
    op.create_table(
        'users',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('surname', sa.String(), nullable=False),
        sa.Column('email', sa.String(), unique=True, nullable=True),
        sa.Column('age', sa.Integer(), nullable=False),
        sa.Column('phone', sa.String(), unique=True, nullable=True),
        sa.Column('role', sa.Enum('admin', 'user', name='userrole'), nullable=False),
        sa.Column('disabled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('password', sa.String(), nullable=False)
    )

    # Добавляем столбец user_id в таблицу appointments
    op.add_column('appointments', sa.Column('user_id', sa.UUID(as_uuid=True), nullable=True))

    # Восстанавливаем внешний ключ для appointments к users
    op.create_foreign_key(
        'appointments_user_id_fkey',  # Имя внешнего ключа
        'appointments',                 # Таблица, в которой находится внешний ключ
        'users',                       # Таблица, на которую ссылается внешний ключ
        ['user_id'],                   # Столбец в appointments
        ['id'],                      # Столбец в users
        ondelete="CASCADE"
    )

def downgrade():
    # Восстанавливаем таблицу clients
    op.create_table(
        'clients',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('surname', sa.String(), nullable=False),
        sa.Column('email', sa.String(), unique=True, nullable=True),
        sa.Column('age', sa.Integer(), nullable=False),
        sa.Column('phone', sa.String(), unique=True, nullable=True)
    )

    # Восстанавливаем внешний ключ для appointments к clients (если необходимо)
    op.create_foreign_key(
        'appointments_client_id_fkey',
        'appointments',
        'clients',
        ['client_id'],  # Имя столбца в appointments
        ['id'],         # Имя столбца в clients
    )

    # Удаляем внешний ключ для appointments к users (если он существует)
    op.drop_constraint('appointments_user_id_fkey', 'appointments', type_='foreignkey')

    # Удаляем столбец user_id из таблицы appointments
    op.drop_column('appointments', 'user_id')

    # Удаляем таблицу users
    op.drop_table('users')
