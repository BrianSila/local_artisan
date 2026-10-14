import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import CheckConstraint
from sqlalchemy import UniqueConstraint
from app.extensions import db

class Booking(db.Model):
    __tablename__ = "bookings"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'accepted', 'dispatched', 'completed', 'cancelled', 'disputed')",
            name="ck_bookings_status",
        ),
    )
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scheduled_date = db.Column(db.DateTime, nullable=False, comment="Date and time of the scheduled job")    
    status = db.Column(db.String(20), nullable=False, default="pending") # pending, accepted, dispatched, completed, cancelled, disputed
    notes = db.Column(db.Text, nullable=True, comment="Custom client instructions or issue descriptions")
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    
    customer_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    artisan_id = db.Column(UUID(as_uuid=True), db.ForeignKey("artisan_profiles.id", ondelete="RESTRICT"), nullable=False)
    service_id = db.Column(UUID(as_uuid=True), db.ForeignKey("artisan_services.id", ondelete="SET NULL"), nullable=True)
    availability_slot_id = db.Column(
        db.Integer,
        db.ForeignKey("artisan_availability_slots.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    customer = db.relationship("User", backref="bookings")
    artisan_profile = db.relationship("ArtisanProfile", backref="bookings")
    service = db.relationship("ArtisanService", backref="bookings")
    availability_slot = db.relationship("AvailabilitySlot", backref="bookings")

    def to_dict(self):
        return {
            "id": str(self.id),
            "scheduled_date": self.scheduled_date.isoformat(),
            "status": self.status,
            "notes": self.notes,
            "customer_id": str(self.customer_id),
            "artisan_id": str(self.artisan_id),
            "service_id": str(self.service_id) if self.service_id else None,
            "availability_slot_id": self.availability_slot_id,
            "created_at": self.created_at.isoformat()
        }

    def __repr__(self):
        return f"<Booking {self.id}>"

class AvailabilitySlot(db.Model):
    __tablename__ = "artisan_availability_slots"
    __table_args__ = (
        CheckConstraint("starts_at < ends_at", name="ck_availability_slot_start_before_end"),
        CheckConstraint("status IN ('available', 'booked')", name="ck_availability_slot_status"),
        UniqueConstraint("artisan_id", "starts_at", name="uq_availability_slot_artisan_start"),
    )

    id = db.Column(db.Integer, primary_key=True)
    artisan_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("artisan_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    starts_at = db.Column(db.DateTime, nullable=False, index=True)
    ends_at = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="available", index=True)

    artisan_profile = db.relationship("ArtisanProfile", backref="availability_slots")

    def to_dict(self):
        return {
            "id": self.id,
            "artisan_id": str(self.artisan_id),
            "starts_at": self.starts_at.isoformat(),
            "ends_at": self.ends_at.isoformat(),
            "status": self.status,
        }

    def __reor__(self):
        return f"<Availability {self.id}>"