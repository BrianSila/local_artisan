import datetime
from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import CheckConstraint

class MpesaTransaction(db.Model):
    __tablename__ = "mpesa_transactions"
    
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)  
    status = db.Column(db.String(20), nullable=False, default="escrow_held")
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    merchant_request_id = db.Column(db.String(100), unique=True, nullable=False)
    checkout_request_id = db.Column(db.String(100), unique=True, nullable=False)
    mpesa_receipt_number = db.Column(db.String(50), unique=True, nullable=True) 

    # A booking may have multiple payment attempts (for example, after a declined STK push).
    booking_id = db.Column(UUID(as_uuid=True), db.ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "booking_id": str(self.booking_id),
            "amount": float(self.amount),
            "phone_number": self.phone_number,
            "status": self.status,
            "mpesa_receipt": self.mpesa_receipt_number,
            "updated_at": self.updated_at.isoformat()
        }
        
    def __repr__(self):
        return f"<Transaction {self.id}>"

class Review(db.Model):
    __tablename__ = "reviews"
    __table_args__ = (
        CheckConstraint("rating BETWEEN 1 AND 5", name="ck_reviews_rating_1_to_5"),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    rating = db.Column(db.Integer, nullable=False)
    
    booking_id = db.Column(UUID(as_uuid=True), db.ForeignKey("bookings.id", ondelete="CASCADE"), unique=True, nullable=False)
    artisan_id = db.Column(UUID(as_uuid=True), db.ForeignKey("artisan_profiles.id", ondelete="CASCADE"), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "booking_id": str(self.booking_id),
            "artisan_id": str(self.artisan_id),
            "rating": self.rating,
            "comment": self.comment,
            "created_at": self.created_at.isoformat()
        }
        
    def __repr__(self):
        return f"<Review {self.id}>"

class Dispute(db.Model):
    __tablename__ = "disputes"
    
    id = db.Column(db.Integer, primary_key=True)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="open") # open, investigating, resoled
    resolution_details = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    booking_id = db.Column(UUID(as_uuid=True), db.ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False)
    raised_by = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "booking_id": str(self.booking_id),
            "raised_by": str(self.raised_by),
            "reason": self.reason,
            "status": self.status,
            "resolution_details": self.resolution_details,
            "created_at": self.created_at.isoformat()
        }

    def __repr__(self):
        return f"<Dispute {self.id}>"