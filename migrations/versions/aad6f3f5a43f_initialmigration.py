"""initialmigration

Revision ID: aad6f3f5a43f
Revises: 56a75f0d9ec8
Create Date: 2017-05-03 15:44:58.941000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'aad6f3f5a43f'
down_revision = '56a75f0d9ec8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('avatar_default', sa.Boolean(), nullable=True))
    op.add_column('users', sa.Column('avatar_url', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'avatar_url')
    op.drop_column('users', 'avatar_default')
    # ### end Alembic commands ###
