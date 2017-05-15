"""empty message

Revision ID: 9da44aebdfdc
Revises: d9735906a937
Create Date: 2017-05-14 02:12:07.551705

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9da44aebdfdc'
down_revision = 'd9735906a937'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('carpoolers',
    sa.Column('tabId', sa.Integer(), nullable=False),
    sa.Column('userId', sa.String(), nullable=True),
    sa.Column('carpoolGroupId', sa.Integer(), nullable=True),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('address', sa.String(), nullable=True),
    sa.Column('preWindow', sa.Integer(), nullable=True),
    sa.Column('need_to_arrive_on_time', sa.Integer(), nullable=True),
    sa.Column('num_seats', sa.Integer(), nullable=True),
    sa.Column('engaged', sa.Integer(), nullable=True),
    sa.Column('state', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('tabId')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('carpoolers')
    # ### end Alembic commands ###
