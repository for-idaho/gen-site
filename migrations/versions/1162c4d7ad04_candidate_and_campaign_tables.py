"""Candidate and Campaign tables

Revision ID: 1162c4d7ad04
Revises: 
Create Date: 2018-03-07 16:13:08.414100

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1162c4d7ad04'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('candidate',
    sa.Column('candidate_id', sa.String(length=32), nullable=False),
    sa.Column('username', sa.String(length=32), nullable=True),
    sa.Column('email', sa.String(length=128), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('create_timestamp', sa.DateTime(), nullable=True),
    sa.Column('last_seen', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('candidate_id')
    )
    op.create_index(op.f('ix_candidate_email'), 'candidate', ['email'], unique=True)
    op.create_index(op.f('ix_candidate_username'), 'candidate', ['username'], unique=True)
    op.create_table('campaign',
    sa.Column('campaign_id', sa.String(length=32), nullable=False),
    sa.Column('candidate_id', sa.String(length=32), nullable=True),
    sa.Column('state', sa.String(length=32), nullable=True),
    sa.Column('district', sa.String(length=32), nullable=True),
    sa.Column('office', sa.String(length=64), nullable=True),
    sa.Column('year', sa.Integer(), nullable=True),
    sa.Column('create_timestamp', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['candidate_id'], ['candidate.candidate_id'], ),
    sa.PrimaryKeyConstraint('campaign_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('campaign')
    op.drop_index(op.f('ix_candidate_username'), table_name='candidate')
    op.drop_index(op.f('ix_candidate_email'), table_name='candidate')
    op.drop_table('candidate')
    # ### end Alembic commands ###
