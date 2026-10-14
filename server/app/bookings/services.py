from datetime import datetime, timezone
from uuid import UUID
from app.extensions import db
from app.bookings.models import AvailabilitySlot, Booking
from app.bookings.schemas import CreateAvailabilitySlotData, CreateBookingData
from app.accounts.models import ArtisanProfile
from app.services.models import ArtisanService
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

    slot = (
        AvailabilitySlot.query.filter_by(id=data["availability_slot_id"])
        .with_for_update()
        .first()
    )
    if slot is None or slot.status != "available":
        raise ValidationError("The selected availability slot is no longer available.")
    if slot.artisan_id != artisan_uuid:
        raise ValidationError("The selected slot does not belong to this artisan.")
    if ArtisanService.query.filter_by(id=service_uuid, artisan_id=artisan_uuid).first() is None:
        raise ValidationError("The selected service does not belong to this artisan.")
    if slot.starts_at <= datetime.utcnow():
        raise ValidationError("The selected availability slot must be in the future.")
    if "scheduled_date" in data:
        requested_date = _to_utc_naive(data["scheduled_date"])
        if requested_date != slot.starts_at:
            raise ValidationError("The scheduled date must match the selected availability slot.")

    new_booking = Booking()
    new_booking.customer_id = customer_uuid
    new_booking.artisan_id = artisan_uuid
    new_booking.service_id = service_uuid
    new_booking.availability_slot_id = slot.id
    new_booking.scheduled_date = slot.starts_at
    new_booking.notes = data.get("notes")
    new_booking.status = "pending"
    slot.status = "booked"
    db.session.add(new_booking)
    db.session.commit()
    return new_booking

def update_booking_workflow_state(actor_id: str, actor_role: str, booking_id: str, new_status: str) -> Booking:
    booking = get_booking_or_404(booking_id)
    allowed_actions = get_allowed_booking_actions(booking, actor_id, actor_role)
    if new_status not in allowed_actions:
        raise ForbiddenError("This booking status transition is not allowed for your account.")

    if new_status == "cancelled" and booking.availability_slot is not None:
        booking.availability_slot.status = "available"
    booking.status = new_status
    db.session.commit()
    return booking


def get_allowed_booking_actions(booking: Booking, actor_id: str, actor_role: str) -> list[str]:
    if actor_role == "customer":
        if str(booking.customer_id) == str(actor_id) and booking.status == "pending":
            return ["cancelled"]
        return []

    artisan_user_id = (
        booking.artisan_profile.user_id if booking.artisan_profile is not None else None
    )
    if actor_role != "artisan" or str(artisan_user_id) != str(actor_id):
        return []

    return {
        "pending": ["accepted", "cancelled"],
        "accepted": ["dispatched", "cancelled"],
        "dispatched": ["completed"],
    }.get(booking.status, [])


def _to_utc_naive(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value
    return value.astimezone(timezone.utc).replace(tzinfo=None)


def create_availability_slot(
    artisan_profile_id: UUID | str,
    data: CreateAvailabilitySlotData,
) -> AvailabilitySlot:
    try:
        profile_uuid = UUID(str(artisan_profile_id))
    except (AttributeError, TypeError, ValueError):
        raise NotFoundError("Artisan profile not found") from None

    profile = (
        ArtisanProfile.query.filter_by(id=profile_uuid)
        .with_for_update()
        .first()
    )
    if profile is None:
        raise NotFoundError("Artisan profile not found")

    starts_at = _to_utc_naive(data["starts_at"])
    ends_at = _to_utc_naive(data["ends_at"])
    if starts_at <= datetime.utcnow():
        raise ValidationError("Availability slots must start in the future.")
    if ends_at <= starts_at:
        raise ValidationError("The slot end time must be after its start time.")

    overlaps = AvailabilitySlot.query.filter(
        AvailabilitySlot.artisan_id == profile_uuid,
        AvailabilitySlot.starts_at < ends_at,
        AvailabilitySlot.ends_at > starts_at,
    ).first()
    if overlaps is not None:
        raise ValidationError("Availability slots cannot overlap.")

    slot = AvailabilitySlot(
        artisan_id=profile_uuid,
        starts_at=starts_at,
        ends_at=ends_at,
        status="available",
    )
    db.session.add(slot)
    db.session.commit()
    return slot


def delete_availability_slot(artisan_profile_id: UUID | str, slot_id: int) -> None:
    slot = AvailabilitySlot.query.filter_by(
        id=slot_id,
        artisan_id=UUID(str(artisan_profile_id)),
    ).first()
    if slot is None:
        raise NotFoundError("Availability slot not found")
    if slot.status == "booked":
        raise ValidationError("A booked availability slot cannot be deleted.")
    db.session.delete(slot)
    db.session.commit()
