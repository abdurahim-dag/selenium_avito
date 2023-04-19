"""create sction table

Revision ID: f98befddc8cf
Revises:
Create Date: 2019-09-17 14:53:04.749244

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f98befddc8cf'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'section',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('status', sa.String(100), nullable=True),
        sa.Column('site', sa.String(100), nullable=True),
        sa.Column('time_stamp', sa.DateTime(timezone=True), nullable=False)
    )

def downgrade():
    op.drop_table('section')
