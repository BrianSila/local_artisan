from typing import cast
from uuid import UUID
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.bookings.schemas import (
    BookingResponseSchema,
    CreateBookingData,
    CreateBookingSchema,
    UpdateBookingStatusData,
    UpdateBookingStatusSchema,
)
from app.bookings.services import create_new_booking, update_booking_workflow_state
from app.bookings.models import Booking
from app.common.pagination import paginate
from app.common.decorators import login_required
from app.common.errors import NotFoundError
from app.extensions import db
from app.accounts.models import User

bookings_bp = Blueprint("bookings", __name__)

create_schema = CreateBookingSchema()
status_schema = UpdateBookingStatusSchema()
booking_response_schema = BookingResponseSchema()

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
    claims = get_jwt()
    role = claims.get("role", "customer")

    if role == "artisan":
        user = db.session.get(User, UUID(str(current_user_id)))
        if user is None or user.artisan_profile is None:
            raise NotFoundError("Artisan profile not found")
        query = Booking.query.filter_by(artisan_id=user.artisan_profile.id)
    else:
        query = Booking.query.filter_by(customer_id=current_user_id)

    query = query.order_by(Booking.created_at.desc())
    
    paginated_history = paginate(query=query, schema=booking_response_schema)
    return jsonify(paginated_history), 200

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
    return jsonify({"message": f"Booking updated to {data['status']}", "booking": updated_booking.to_dict()}), 200
