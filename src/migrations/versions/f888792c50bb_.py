"""empty message

Revision ID: f888792c50bb
Revises: 2632481d9007
Create Date: 2017-05-18 05:08:49.606823

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f888792c50bb'
down_revision = '2632481d9007'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('carpooler', sa.Column('fieldstate', sa.String(), nullable=True))
    op.add_column('carpooler', sa.Column('on_time', sa.Integer(), nullable=True))
    op.drop_column('carpooler', 'state')
    op.drop_column('carpooler', 'need_to_arrive_on_time')
    op.add_column('pool', sa.Column('latenessWindow', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('pool', 'latenessWindow')
    op.add_column('carpooler', sa.Column('need_to_arrive_on_time', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('carpooler', sa.Column('state', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_column('carpooler', 'on_time')
    op.drop_column('carpooler', 'fieldstate')
    # ### end Alembic commands ###
