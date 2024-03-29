"""added family friendly tables

Revision ID: 2e5b5e7bf251
Revises: 7d6ee6e3ad0a
Create Date: 2022-08-16 11:13:05.956556

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2e5b5e7bf251'
down_revision = '7d6ee6e3ad0a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('family_friendly_channels',
    sa.Column('server_id', sa.Integer(), nullable=False),
    sa.Column('channel_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['server_id'], ['servers.server_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('channel_id')
    )
    op.create_table('prohibited_words',
    sa.Column('server_id', sa.Integer(), nullable=False),
    sa.Column('word', sa.Text(), nullable=False),
    sa.ForeignKeyConstraint(['server_id'], ['servers.server_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('server_id', 'word')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('prohibited_words')
    op.drop_table('family_friendly_channels')
    # ### end Alembic commands ###
