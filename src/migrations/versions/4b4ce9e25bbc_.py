"""empty message

Revision ID: 4b4ce9e25bbc
Revises: 
Create Date: 2017-08-25 01:06:10.868882

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4b4ce9e25bbc'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('pool',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('poolName', sa.String(), nullable=True),
    sa.Column('eventDate', sa.String(), nullable=True),
    sa.Column('eventTime', sa.String(), nullable=True),
    sa.Column('eventDateTime', sa.DateTime(), nullable=True),
    sa.Column('latenessWindow', sa.Integer(), nullable=True),
    sa.Column('eventAddress', sa.String(), nullable=True),
    sa.Column('eventContact', sa.String(), nullable=True),
    sa.Column('eventEmail', sa.String(), nullable=True),
    sa.Column('eventHostOrg', sa.String(), nullable=True),
    sa.Column('signature', sa.String(), nullable=True),
    sa.Column('fireNotice', sa.String(), nullable=True),
    sa.Column('selfRep', sa.Text(), nullable=True),
    sa.Column('selfFormalRep', sa.Text(), nullable=True),
    sa.Column('noticeWentOut', sa.Boolean(), nullable=True),
    sa.Column('optimizedYet', sa.Boolean(), nullable=True),
    sa.Column('optimizationCurrent', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('teams',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('password', sa.String(), nullable=True),
    sa.Column('city', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('carpooler',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('session_id', sa.String(length=36), nullable=True),
    sa.Column('password', sa.String(), nullable=True),
    sa.Column('current_pool_id', sa.Integer(), nullable=True),
    sa.Column('fbId', sa.String(), nullable=True),
    sa.Column('selfRep', sa.Text(), nullable=True),
    sa.Column('selfFormalRep', sa.Text(), nullable=True),
    sa.Column('fieldstate', sa.String(), nullable=True),
    sa.Column('firstname', sa.String(), nullable=True),
    sa.Column('lastname', sa.String(), nullable=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('menu', sa.String(), nullable=True),
    sa.Column('mode', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['current_pool_id'], ['pool.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('session_id')
    )
    op.create_table('team_affiliation',
    sa.Column('pool_id', sa.Integer(), nullable=False),
    sa.Column('team_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['pool_id'], ['pool.id'], ),
    sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ),
    sa.PrimaryKeyConstraint('pool_id', 'team_id')
    )
    op.create_table('team_membership',
    sa.Column('carpooler_id', sa.Integer(), nullable=False),
    sa.Column('team_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['carpooler_id'], ['carpooler.id'], ),
    sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ),
    sa.PrimaryKeyConstraint('carpooler_id', 'team_id')
    )
    op.create_table('trips',
    sa.Column('carpooler_id', sa.Integer(), nullable=False),
    sa.Column('pool_id', sa.Integer(), nullable=False),
    sa.Column('address', sa.String(), nullable=True),
    sa.Column('num_seats', sa.Integer(), nullable=True),
    sa.Column('preWindow', sa.Integer(), nullable=True),
    sa.Column('on_time', sa.Integer(), nullable=True),
    sa.Column('must_drive', sa.Integer(), nullable=True),
    sa.Column('selfRep', sa.Text(), nullable=True),
    sa.Column('selfFormalRep', sa.Text(), nullable=True),
    sa.Column('poolRepLoaded', sa.Integer(), nullable=True),
    sa.Column('carpoolerRepLoaded', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['carpooler_id'], ['carpooler.id'], ),
    sa.ForeignKeyConstraint(['pool_id'], ['pool.id'], ),
    sa.PrimaryKeyConstraint('carpooler_id', 'pool_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('trips')
    op.drop_table('team_membership')
    op.drop_table('team_affiliation')
    op.drop_table('carpooler')
    op.drop_table('teams')
    op.drop_table('pool')
    # ### end Alembic commands ###
