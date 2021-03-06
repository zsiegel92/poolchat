"""empty message

Revision ID: 227790f61123
Revises: e7cdb8cb1428
Create Date: 2017-09-01 12:23:03.414920

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '227790f61123'
down_revision = 'e7cdb8cb1428'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('instruction',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('pool_id', sa.Integer(), nullable=True),
    sa.Column('instruction', sa.Text(), nullable=True),
    sa.Column('dateTime', sa.DateTime(), nullable=True),
    sa.Column('success', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['pool_id'], ['pool.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('instruction')
    # ### end Alembic commands ###
