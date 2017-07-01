"""empty message

Revision ID: bee4994c9b79
Revises: 26f02e2d18d3
Create Date: 2017-06-20 14:46:53.584406

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bee4994c9b79'
down_revision = '26f02e2d18d3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('pool', sa.Column('selfFormalRep', sa.Text(), nullable=True))
    op.add_column('pool', sa.Column('selfRep', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('pool', 'selfRep')
    op.drop_column('pool', 'selfFormalRep')
    # ### end Alembic commands ###