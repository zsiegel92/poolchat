"""empty message

Revision ID: e7cdb8cb1428
Revises: d00b2dfdd556
Create Date: 2017-08-31 23:29:06.164600

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e7cdb8cb1428'
down_revision = 'd00b2dfdd556'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('temp_teams', sa.Column('approved', sa.Boolean(), nullable=True))
    op.add_column('temp_teams', sa.Column('confirmed_email', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('temp_teams', 'confirmed_email')
    op.drop_column('temp_teams', 'approved')
    # ### end Alembic commands ###