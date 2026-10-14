"""Add customer saved artisans

Revision ID: eb2f65830f4b
Revises: cd942e18b607
Create Date: 2026-10-14

"""
from alembic import op
import sqlalchemy as sa


revision = "eb2f65830f4b"
down_revision = "cd942e18b607"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "saved_artisans",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("customer_id", sa.Uuid(), nullable=False),
        sa.Column("artisan_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["artisan_id"], ["artisan_profiles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["customer_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("customer_id", "artisan_id", name="uq_saved_artisan_customer_profile"),
    )


def downgrade():
    op.drop_table("saved_artisans")