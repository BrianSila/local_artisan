import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import CheckConstraint
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

    customer = db.relationship("User", backref="bookings")
    artisan_profile = db.relationship("ArtisanProfile", backref="bookings")
    service = db.relationship("ArtisanService", backref="bookings")

    def to_dict(self):
        return {
            "id": str(self.id),
            "scheduled_date": self.scheduled_date.isoformat(),
            "status": self.status,
            "notes": self.notes,
            "customer_id": str(self.customer_id),
            "artisan_id": str(self.artisan_id),
            "service_id": str(self.service_id) if self.service_id else None,
            "created_at": self.created_at.isoformat()
        }

    def __repr__(self):
        return f"<Booking {self.id}>"