from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from typing import cast
from app.operations.schemas import (
    DisputeResponseSchema,
    FileDisputeData,
    FileDisputeSchema,
    MpesaCheckoutData,
    MpesaCheckoutResponseSchema,
    MpesaCheckoutSchema,
    ReviewResponseSchema,
    SubmitReviewData,
    SubmitReviewSchema,
)
from app.operations.services import process_mpesa_stk_mock, add_booking_review, log_booking_dispute
from app.common.decorators import login_required

operations_bp = Blueprint("operations", __name__)

review_schema = SubmitReviewSchema()
dispute_schema = FileDisputeSchema()
checkout_schema = MpesaCheckoutSchema()
checkout_response_schema = MpesaCheckoutResponseSchema()
review_response_schema = ReviewResponseSchema()
dispute_response_schema = DisputeResponseSchema()

@operations_bp.route("/checkout/<string:booking_id>", methods=["POST"])
@jwt_required()
@login_required
def initiate_checkout(booking_id):
    json_data = request.get_json() or {}
    data = cast(MpesaCheckoutData, checkout_schema.load(json_data))
    
    response = process_mpesa_stk_mock(booking_id, data["phone_number"])
    return jsonify(checkout_response_schema.dump(response)), 200

@operations_bp.route("/bookings/<string:booking_id>/review", methods=["POST"])
@jwt_required()
@login_required
def submit_review(booking_id):
    json_data = request.get_json() or {}
    data = cast(SubmitReviewData, review_schema.load(json_data))
    
    current_user_id = get_jwt_identity()
    review = add_booking_review(current_user_id, booking_id, data)
    return jsonify({
        "message": "Review submitted successfully",
        "review": review_response_schema.dump(review.to_dict()),
    }), 201

@operations_bp.route("/bookings/<string:booking_id>/dispute", methods=["POST"])
@jwt_required()
@login_required
def file_dispute(booking_id):
    json_data = request.get_json() or {}
    data = cast(FileDisputeData, dispute_schema.load(json_data))
    
    current_user_id = get_jwt_identity()
    dispute = log_booking_dispute(current_user_id, booking_id, data)
    return jsonify({
        "message": "Dispute filed. Escrow has been frozen pending admin review",
        "dispute": dispute_response_schema.dump(dispute.to_dict()),
    }), 201
