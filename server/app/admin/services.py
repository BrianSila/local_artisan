from datetime import datetime
from uuid import UUID
from app.extensions import db
from app.accounts.models import User, ArtisanProfile
from app.operations.models import Dispute, MpesaTransaction
from app.bookings.models import Booking
from app.admin.schemas import ResolveDisputeData
from app.common.errors import NotFoundError, ValidationError

def get_admin_dashboard_stats() -> dict:
    return {
        "total_users": User.query.count(),
        "total_artisans": ArtisanProfile.query.count(),
        "verified_artisans": ArtisanProfile.query.filter_by(is_verified=True).count(),
        "active_disputes": Dispute.query.filter_by(status="open").count()
    }

def toggle_artisan_verification_status(profile_id: UUID | str, is_verified: bool) -> ArtisanProfile:
    try:
        profile_uuid = UUID(str(profile_id))
    except (AttributeError, TypeError, ValueError):
        raise NotFoundError("The specified artisan profile does not exist.") from None

    profile = db.session.get(ArtisanProfile, profile_uuid)
    if not profile:
        raise NotFoundError("The specified artisan profile records do not exist.")
        
    profile.is_verified = is_verified
    db.session.commit()
    return profile

def update_user_suspension_state(user_id: UUID | str, is_blocked: bool) -> User:
    try:
        user_uuid = UUID(str(user_id))
    except (AttributeError, TypeError, ValueError):
        raise NotFoundError("Target user account not found.") from None

    user = db.session.get(User, user_uuid)
    if not user:
        raise NotFoundError("Target user account not found.")
    if user.role == "admin":
        raise ValidationError("Platform constraints block actions targeting other administrators.")
        
    user.is_blocked = is_blocked
    db.session.commit()
    return user

def process_dispute_resolution(dispute_id: int, resolution_data: ResolveDisputeData) -> Dispute:
    dispute = db.session.get(Dispute, dispute_id)
    if not dispute:
        raise NotFoundError("Target dispute record context missing.")
    if dispute.status == "resolved":
        raise ValidationError("This dispute case entry has already been permanently resolved.")

    dispute.status = "resolved"
    dispute.resolution_details = resolution_data["resolution_details"]

    booking = db.session.get(Booking, dispute.booking_id)
    if booking is None:
        raise NotFoundError("Booking associated with this dispute was not found.")

    payment = (
        MpesaTransaction.query.filter_by(booking_id=booking.id)
        .order_by(MpesaTransaction.updated_at.desc(), MpesaTransaction.id.desc())
        .first()
    )
    
    if payment:
        payout_rule = resolution_data["resolution_status"]
        payment.status = payout_rule
        
        booking.status = "completed" if payout_rule == "released_to_fundi" else "cancelled"

    db.session.commit()
    return dispute
