"""create urls table

Revision ID: 1bf5f353b3e3
Revises: ca9700b82d8e
Create Date: 2020-07-13 09:18:33.220761

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1bf5f353b3e3'
down_revision = 'ca9700b82d8e'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'avito_ad_urls',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('url', sa.String(1000), nullable=True),
        sa.Column('avito_id', sa.BIGINT, nullable=True),
        sa.Column('status', sa.String(20), nullable=True),
        sa.Column('tablez', sa.String(100), nullable=True),
        sa.Column('locality', sa.String(200), nullable=True),
        sa.Column('time_stamp', sa.DateTime(timezone=True), nullable=True),
        sa.Column('section_id', sa.Integer, sa.ForeignKey("section.id"))
    )
    op.create_index('avito_ad_urls_avito_id_time_stamp', 'avito_ad_urls', ['avito_id', 'time_stamp'], unique=True)

def downgrade():
    op.drop_table('avito_ad_urls')
