"""Add artisan availability slots

Revision ID: cd942e18b607
Revises: bf61321d7c49
Create Date: 2026-10-14

"""
from alembic import op
import sqlalchemy as sa


revision = "cd942e18b607"
down_revision = "bf61321d7c49"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "artisan_availability_slots",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("artisan_id", sa.Uuid(), nullable=False),
        sa.Column("starts_at", sa.DateTime(), nullable=False),
        sa.Column("ends_at", sa.DateTime(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.CheckConstraint("starts_at < ends_at", name="ck_availability_slot_start_before_end"),
        sa.CheckConstraint("status IN ('available', 'booked')", name="ck_availability_slot_status"),
        sa.ForeignKeyConstraint(["artisan_id"], ["artisan_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("artisan_id", "starts_at", name="uq_availability_slot_artisan_start"),
    )
    op.create_index("ix_artisan_availability_slots_artisan_id", "artisan_availability_slots", ["artisan_id"])
    op.create_index("ix_artisan_availability_slots_starts_at", "artisan_availability_slots", ["starts_at"])
    op.create_index("ix_artisan_availability_slots_status", "artisan_availability_slots", ["status"])
    with op.batch_alter_table("bookings") as batch_op:
        batch_op.add_column(sa.Column("availability_slot_id", sa.Integer(), nullable=True))
        batch_op.create_index("ix_bookings_availability_slot_id", ["availability_slot_id"])
        batch_op.create_foreign_key(
            "fk_bookings_availability_slot_id_artisan_availability_slots",
            "artisan_availability_slots",
            ["availability_slot_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade():
    with op.batch_alter_table("bookings") as batch_op:
        batch_op.drop_constraint(
            "fk_bookings_availability_slot_id_artisan_availability_slots",
            type_="foreignkey",
        )
        batch_op.drop_index("ix_bookings_availability_slot_id")
        batch_op.drop_column("availability_slot_id")
    op.drop_index("ix_artisan_availability_slots_status", table_name="artisan_availability_slots")
    op.drop_index("ix_artisan_availability_slots_starts_at", table_name="artisan_availability_slots")
    op.drop_index("ix_artisan_availability_slots_artisan_id", table_name="artisan_availability_slots")
    op.drop_table("artisan_availability_slots")