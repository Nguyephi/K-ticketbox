"""empty message

Revision ID: 8f0e37ebbd52
Revises: d22ab8e0217f
Create Date: 2019-07-07 20:02:39.875282

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8f0e37ebbd52'
down_revision = 'd22ab8e0217f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('events', 'start',
               existing_type=sa.DATE(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('events', 'start',
               existing_type=sa.DATE(),
               nullable=True)
    # ### end Alembic commands ###
