"""empty message

Revision ID: e3a6f0210814
Revises: 80db1fd4ee9d
Create Date: 2017-08-07 10:45:21.044894

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e3a6f0210814'
down_revision = '80db1fd4ee9d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('pool', sa.Column('noticeWentOut', sa.Boolean(), nullable=True))
    op.add_column('pool', sa.Column('optimizedYet', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('pool', 'optimizedYet')
    op.drop_column('pool', 'noticeWentOut')
    # ### end Alembic commands ###
