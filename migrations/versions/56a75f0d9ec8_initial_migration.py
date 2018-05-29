"""initial migration

Revision ID: 56a75f0d9ec8
Revises: 1db8081f3958
Create Date: 2017-04-19 22:25:42.406000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '56a75f0d9ec8'
down_revision = '1db8081f3958'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('about_me', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('gender', sa.String(length=8), nullable=True))
    op.add_column('users', sa.Column('location', sa.String(length=128), nullable=True))
    op.add_column('users', sa.Column('member_since', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'member_since')
    op.drop_column('users', 'location')
    op.drop_column('users', 'gender')
    op.drop_column('users', 'about_me')
    # ### end Alembic commands ###
