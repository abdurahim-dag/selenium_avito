"""add table avito sales commercial

Revision ID: 033befcd0f2e
Revises: a368ef6b40f7
Create Date: 2019-09-19 12:45:56.714560

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '033befcd0f2e'
down_revision = 'a368ef6b40f7'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'avito_ad_sales_commercial',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(200), nullable=True),
        sa.Column('address', sa.String(200), nullable=True),
        sa.Column('price_value', sa.Float, nullable=True),
        sa.Column('price_currency', sa.String(50), nullable=True),
        sa.Column('price_original', sa.String(200), nullable=True),
        sa.Column('x', sa.Float, nullable=True),
        sa.Column('y', sa.Float, nullable=True),
        sa.Column('square_value', sa.Float, nullable=True),
        sa.Column('square_currency', sa.String(50), nullable=True),
        sa.Column('square_original', sa.String(50), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('other', sa.Text(), nullable=True),
        sa.Column('screenshot_file', sa.String(200), nullable=True),
        sa.Column('url', sa.String(500), nullable=True),
        sa.Column('phone', sa.String(100), nullable=True),
        sa.Column('avito_id', sa.BIGINT, nullable=True),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('locality', sa.String(100), nullable=True),

        sa.Column('time_stamp', sa.DateTime(timezone=True), nullable=False),

        sa.Column('section_id', sa.Integer, sa.ForeignKey("section.id"))
    )

    op.create_index('avito_ad_sales_commercial_avito_id_time_stamp', 'avito_ad_sales_commercial', ['avito_id', 'time_stamp'], unique=True)

def downgrade():
    op.drop_table('avito_ad_sales_commercial')
