"""Add artisan coordinates for nearby marketplace search

Revision ID: 7c1e94b8a2f0
Revises: 33818bbaf8f5
Create Date: 2026-10-07

"""
from alembic import op
import sqlalchemy as sa


revision = "7c1e94b8a2f0"
down_revision = "33818bbaf8f5"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("artisan_profiles", sa.Column("latitude", sa.Float(), nullable=True))
    op.add_column("artisan_profiles", sa.Column("longitude", sa.Float(), nullable=True))
    with op.batch_alter_table("artisan_profiles") as batch_op:
        batch_op.create_check_constraint(
            "ck_artisan_profiles_coordinates_pair",
            "((latitude IS NULL AND longitude IS NULL) OR "
            "(latitude IS NOT NULL AND longitude IS NOT NULL))",
        )
        batch_op.create_check_constraint(
            "ck_artisan_profiles_latitude_range",
            "latitude IS NULL OR latitude BETWEEN -90 AND 90",
        )
        batch_op.create_check_constraint(
            "ck_artisan_profiles_longitude_range",
            "longitude IS NULL OR longitude BETWEEN -180 AND 180",
        )


def downgrade():
    with op.batch_alter_table("artisan_profiles") as batch_op:
        batch_op.drop_constraint("ck_artisan_profiles_longitude_range", type_="check")
        batch_op.drop_constraint("ck_artisan_profiles_latitude_range", type_="check")
        batch_op.drop_constraint("ck_artisan_profiles_coordinates_pair", type_="check")
    op.drop_column("artisan_profiles", "longitude")
    op.drop_column("artisan_profiles", "latitude")