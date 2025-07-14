"""add_reset_token_fields

Revision ID: f3d6f88fea3a
Revises: 76edf4897510
Create Date: 2025-07-11 18:44:03.593417

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f3d6f88fea3a'
down_revision: Union[str, None] = '76edf4897510'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Добавьте USING для явного преобразования данных
    op.alter_column('appointments', 'date',
                    existing_type=sa.INTEGER(),
                    type_=sa.Date(),
                    postgresql_using='(timestamp \'1970-01-01\' + date * interval \'1 day\')::date',
                    existing_nullable=False)

    # Остальные изменения (добавление reset_token и reset_token_expires)
    op.add_column('users', sa.Column('reset_token', sa.String(), nullable=True))
    op.add_column('users', sa.Column('reset_token_expires', sa.DateTime(), nullable=True))


def downgrade():
    # Для отката также нужно явное преобразование
    op.alter_column('appointments', 'date',
                    existing_type=sa.Date(),
                    type_=sa.INTEGER(),
                    postgresql_using='extract(epoch from date)::integer',
                    existing_nullable=False)

    op.drop_column('users', 'reset_token_expires')
    op.drop_column('users', 'reset_token')
    # ### end Alembic commands ###
