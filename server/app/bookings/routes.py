from typing import cast
from uuid import UUID
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.bookings.schemas import (
    AvailabilitySlotSchema,
    CreateAvailabilitySlotData,
    CreateAvailabilitySlotSchema,
    BookingResponseSchema,
    CreateBookingData,
    CreateBookingSchema,
    UpdateBookingStatusData,
    UpdateBookingStatusSchema,
)
from app.bookings.services import (
    create_availability_slot,
    create_new_booking,
    delete_availability_slot,
    get_allowed_booking_actions,
    update_booking_workflow_state,
)
from app.bookings.models import AvailabilitySlot, Booking
from app.common.pagination import paginate
from app.common.decorators import login_required, role_required
from app.common.errors import NotFoundError
from app.extensions import db
from app.accounts.models import User

bookings_bp = Blueprint("bookings", __name__)

create_schema = CreateBookingSchema()
availability_create_schema = CreateAvailabilitySlotSchema()
availability_list_schema = AvailabilitySlotSchema(many=True)
status_schema = UpdateBookingStatusSchema()
booking_response_schema = BookingResponseSchema()


@bookings_bp.route("/availability", methods=["GET"])
@jwt_required()
@role_required("artisan")
def list_artisan_availability():
    current_user_id = get_jwt_identity()
    user = db.session.get(User, UUID(str(current_user_id)))
    if user is None or user.artisan_profile is None:
        raise NotFoundError("Artisan profile not found")
    slots = (
        AvailabilitySlot.query.filter_by(artisan_id=user.artisan_profile.id)
        .order_by(AvailabilitySlot.starts_at.asc())
        .all()
    )
    return jsonify(availability_list_schema.dump(slots)), 200


@bookings_bp.route("/availability", methods=["POST"])
@jwt_required()
@role_required("artisan")
def create_artisan_availability():
    data = cast(CreateAvailabilitySlotData, availability_create_schema.load(request.get_json() or {}))
    current_user_id = get_jwt_identity()
    user = db.session.get(User, UUID(str(current_user_id)))
    if user is None or user.artisan_profile is None:
        raise NotFoundError("Artisan profile not found")
    slot = create_availability_slot(user.artisan_profile.id, data)
    return jsonify({"slot": slot.to_dict()}), 201


@bookings_bp.route("/availability/<int:slot_id>", methods=["DELETE"])
@jwt_required()
@role_required("artisan")
def remove_artisan_availability(slot_id):
    current_user_id = get_jwt_identity()
    user = db.session.get(User, UUID(str(current_user_id)))
    if user is None or user.artisan_profile is None:
        raise NotFoundError("Artisan profile not found")
    delete_availability_slot(user.artisan_profile.id, slot_id)
    return jsonify({"message": "Availability slot deleted successfully"}), 200

@bookings_bp.route("", methods=["POST"])
@jwt_required()
@login_required
def request_booking():
    json_data = request.get_json() or {}
    data = cast(CreateBookingData, create_schema.load(json_data))
    
    current_user_id = get_jwt_identity()
    booking = create_new_booking(current_user_id, data)
    return jsonify({"message": "Booking request sent successfully", "booking": booking.to_dict()}), 201

@bookings_bp.route("/history", methods=["GET"])
@jwt_required()
@login_required
def get_user_bookings_history():
    current_user_id = get_jwt_identity()
    current_user_uuid = UUID(str(current_user_id))
    claims = get_jwt()
    role = claims.get("role", "customer")

    if role == "artisan":
        user = db.session.get(User, UUID(str(current_user_id)))
        if user is None or user.artisan_profile is None:
            raise NotFoundError("Artisan profile not found")
        query = Booking.query.filter_by(artisan_id=user.artisan_profile.id)
    else:
        query = Booking.query.filter_by(customer_id=current_user_uuid)

    query = query.order_by(Booking.created_at.desc())
    
    page = request.args.get("page", 1, type=int)
    limit = min(request.args.get("limit", 20, type=int), 100)
    pagination = query.paginate(page=page, per_page=limit, error_out=False)
    items = booking_response_schema.dump(pagination.items, many=True)
    for booking, item in zip(pagination.items, items):
        item["allowed_actions"] = get_allowed_booking_actions(
            booking,
            current_user_id,
            role,
        )
    return jsonify({
        "total": pagination.total,
        "page": pagination.page,
        "pages": pagination.pages,
        "items": items,
    }), 200

@bookings_bp.route("/<uuid:booking_id>/status", methods=["PATCH"])
@jwt_required()
@login_required
def patch_booking_status(booking_id):
    json_data = request.get_json() or {}
    data = cast(UpdateBookingStatusData, status_schema.load(json_data))
    
    current_user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get("role", "customer")

    updated_booking = update_booking_workflow_state(
        actor_id=current_user_id,
        actor_role=role,
        booking_id=booking_id,
        new_status=data["status"]
    )
    booking_data = booking_response_schema.dump(updated_booking)
    booking_data["allowed_actions"] = get_allowed_booking_actions(
        updated_booking,
        current_user_id,
        role,
    )
    return jsonify({"message": f"Booking updated to {data['status']}", "booking": booking_data}), 200
