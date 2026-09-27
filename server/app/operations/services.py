from app.extensions import db
from app.operations.models import MpesaTransaction, Review, Dispute
from app.bookings.services import get_booking_or_404
from app.common.errors import ForbiddenError, ValidationError
from app.operations.schemas import (
    FileDisputeData,
    MpesaCheckoutResponseData,
    SubmitReviewData,
)
from uuid import uuid4

def process_mpesa_stk_mock(booking_id: str, phone_number: str) -> MpesaCheckoutResponseData:
    """Simulates initiating an M-Pesa STK Push payment callback tracking footprint"""
    booking = get_booking_or_404(booking_id)
        
    # Mocking standard Safaricom API response parameters
    merchant_id = f"MRCH_{uuid4().hex}"
    checkout_id = f"CHCK_{uuid4().hex}"
    
    transaction = MpesaTransaction()
    transaction.booking_id = booking.id
    transaction.amount = 1500.00  # Mock base fee in KES
    transaction.phone_number = phone_number
    transaction.merchant_request_id = merchant_id
    transaction.checkout_request_id = checkout_id
    transaction.status = "escrow_held"
    
    db.session.add(transaction)
    db.session.commit()
    
    return {
        "merchant_request_id": merchant_id,
        "checkout_request_id": checkout_id,
        "response_description": "Success. Request accepted for processing",
    }

def add_booking_review(customer_id: str, booking_id: str, data: SubmitReviewData) -> Review:
    booking = get_booking_or_404(booking_id)
    if str(booking.customer_id) != str(customer_id):
        raise ForbiddenError("You cannot review a job you did not request")
    if booking.status != "completed":
        raise ValidationError("Reviews can only be submitted for completed tasks")
        
    review = Review()
    review.booking_id = booking.id
    review.artisan_id = booking.artisan_id
    review.rating = data["rating"]
    review.comment = data.get("comment")
    db.session.add(review)
    db.session.commit()
    return review

def log_booking_dispute(user_id: str, booking_id: str, data: FileDisputeData) -> Dispute:
    booking = get_booking_or_404(booking_id)

    artisan_user_id = (
        booking.artisan_profile.user_id if booking.artisan_profile is not None else None
    )
    if str(user_id) not in {str(booking.customer_id), str(artisan_user_id)}:
        raise ForbiddenError("Only a customer or the assigned artisan can dispute this booking")
        
    # Freezes the job immediately
    booking.status = "disputed"
    
    dispute = Dispute()
    dispute.booking_id = booking.id
    dispute.raised_by = user_id
    dispute.reason = data["reason"]
    dispute.status = "open"
    db.session.add(dispute)
    db.session.commit()
    return dispute
