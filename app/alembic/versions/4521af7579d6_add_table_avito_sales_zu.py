"""add table avito sales zu

Revision ID: 4521af7579d6
Revises: f98befddc8cf
Create Date: 2019-09-19 12:25:35.315529

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4521af7579d6'
down_revision = 'f98befddc8cf'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'avito_ad_sales_zu',
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
        sa.Column('to_city', sa.String(100), nullable=True),

        sa.Column('time_stamp', sa.DateTime(timezone=True), nullable=False),

        sa.Column('section_id', sa.Integer, sa.ForeignKey("section.id"))
    )

    op.create_index('avito_ad_sales_zu_avito_id_time_stamp', 'avito_ad_sales_zu', ['avito_id', 'time_stamp'], unique=True)

def downgrade():
    op.drop_table('avito_ad_sales_zu')
