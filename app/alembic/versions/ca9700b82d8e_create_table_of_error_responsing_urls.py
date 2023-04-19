"""create table of error responsing urls

Revision ID: ca9700b82d8e
Revises: 033befcd0f2e
Create Date: 2019-09-26 13:45:39.458941

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ca9700b82d8e'
down_revision = '033befcd0f2e'
branch_labels = None
depends_on = None


def upgrade():
        op.create_table(
        'avito_error',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('status', sa.String(100), nullable=True),
        sa.Column('urls', sa.Text(), nullable=True),
        sa.Column('time_stamp', sa.DateTime(timezone=True), nullable=False)
    )


def downgrade():
    op.drop_table('avito_error')
