"""Add artisan work photo gallery

Revision ID: bf61321d7c49
Revises: 7c1e94b8a2f0
Create Date: 2026-10-14

"""
from alembic import op
import sqlalchemy as sa


revision = "bf61321d7c49"
down_revision = "7c1e94b8a2f0"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "artisan_profiles",
        sa.Column("work_photos", sa.JSON(), nullable=False, server_default="[]"),
    )


def downgrade():
    op.drop_column("artisan_profiles", "work_photos")