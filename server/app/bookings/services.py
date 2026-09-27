from uuid import UUID
from app.extensions import db
from app.bookings.models import Booking
from app.bookings.schemas import CreateBookingData
from app.common.errors import NotFoundError, ForbiddenError, ValidationError

def get_booking_or_404(booking_id: UUID | str) -> Booking:
    try:
        booking_uuid = UUID(str(booking_id))
    except (AttributeError, TypeError, ValueError):
        raise NotFoundError("The requested booking record does not exist.") from None

    booking = db.session.get(Booking, booking_uuid)
    if not booking:
        raise NotFoundError("The requested booking record does not exist.")
    return booking

def create_new_booking(customer_id: UUID | str, data: CreateBookingData) -> Booking:
    try:
        customer_uuid = UUID(str(customer_id))
        artisan_uuid = UUID(str(data["artisan_id"]))
        service_uuid = UUID(str(data["service_id"]))
    except (AttributeError, TypeError, ValueError):
        raise ValidationError("Booking identifiers must be valid UUIDs.") from None

    new_booking = Booking()
    new_booking.customer_id = customer_uuid
    new_booking.artisan_id = artisan_uuid
    new_booking.service_id = service_uuid
    new_booking.scheduled_date = data["scheduled_date"]
    new_booking.notes = data.get("notes")
    new_booking.status = "pending"
    db.session.add(new_booking)
    db.session.commit()
    return new_booking

def update_booking_workflow_state(actor_id: str, actor_role: str, booking_id: str, new_status: str) -> Booking:
    booking = get_booking_or_404(booking_id)

    if actor_role == "customer" and str(booking.customer_id) != str(actor_id):
        raise ForbiddenError("Unauthorized access to this booking contract.")
    if actor_role == "artisan" and str(booking.artisan_profile.user_id if booking.artisan_profile else '') != str(actor_id):
        raise ForbiddenError("You cannot modify jobs assigned to other artisans.")

    if booking.status in ["completed", "cancelled"]:
        raise ValidationError(f"Cannot update state. This job has already been closed as {booking.status}.")

    if actor_role == "customer" and new_status != "cancelled":
        raise ForbiddenError("Customers can only update status to cancelled.")

    booking.status = new_status
    db.session.commit()
    return booking
