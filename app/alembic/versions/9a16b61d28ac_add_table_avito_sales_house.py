"""add table avito sales house

Revision ID: 9a16b61d28ac
Revises: a865f2105d9f
Create Date: 2019-09-19 12:29:59.019327

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9a16b61d28ac'
down_revision = 'a865f2105d9f'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'avito_ad_sales_house',
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
        sa.Column('wall', sa.String(100), nullable=True),
        sa.Column('to_city', sa.String(100), nullable=True),
        sa.Column('floors', sa.Integer, nullable=True),
        sa.Column('square_zu', sa.String(100), nullable=True),

        sa.Column('time_stamp', sa.DateTime(timezone=True), nullable=False),

        sa.Column('section_id', sa.Integer, sa.ForeignKey("section.id"))
    )
    op.create_index('avito_ad_sales_house_avito_id_time_stamp', 'avito_ad_sales_house', ['avito_id', 'time_stamp'], unique=True)

def downgrade():
    op.drop_table('avito_ad_sales_house')
