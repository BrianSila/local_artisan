from typing import cast
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.common.decorators import login_required, role_required
from app.admin.schemas import (
    DisputeResponseSchema,
    ResolveDisputeData,
    ResolveDisputeSchema,
    SuspendUserData,
    SuspendUserSchema,
    VerifyArtisanData,
    VerifyArtisanSchema,
)
from app.admin.services import (
    get_admin_dashboard_stats, 
    toggle_artisan_verification_status, 
    update_user_suspension_state, 
    process_dispute_resolution
)
from app.operations.models import Dispute
from app.common.pagination import paginate

admin_bp = Blueprint("admin_controls", __name__)

verify_schema = VerifyArtisanSchema()
suspend_schema = SuspendUserSchema()
resolve_schema = ResolveDisputeSchema()
dispute_output_schema = DisputeResponseSchema()

@admin_bp.route("/dashboard/stats", methods=["GET"])
@jwt_required()
@role_required("admin")
def get_stats():
    stats = get_admin_dashboard_stats()
    return jsonify(stats), 200

@admin_bp.route("/artisans/<uuid:profile_id>/verify", methods=["PATCH"])
@jwt_required()
@role_required("admin")
def patch_artisan_verification(profile_id):
    json_data = request.get_json() or {}
    data = cast(VerifyArtisanData, verify_schema.load(json_data))
    
    profile = toggle_artisan_verification_status(profile_id, data["is_verified"])
    return jsonify({"message": "Artisan verification updated successfully.", "profile": profile.to_dict()}), 200

@admin_bp.route("/users/<uuid:user_id>/suspend", methods=["PATCH"])
@jwt_required()
@role_required("admin")
def patch_user_suspension(user_id):
    json_data = request.get_json() or {}
    data = cast(SuspendUserData, suspend_schema.load(json_data))
    
    user = update_user_suspension_state(user_id, data["is_blocked"])
    return jsonify({"message": f"User suspension status adjusted to {data['is_blocked']}.", "user": user.to_dict()}), 200

@admin_bp.route("/disputes", methods=["GET"])
@jwt_required()
@role_required("admin")
def list_platform_disputes():
    query = Dispute.query.filter_by(status="open").order_by(Dispute.created_at.asc())
    
    paginated_disputes = paginate(query=query, schema=dispute_output_schema)
    return jsonify(paginated_disputes), 200

@admin_bp.route("/disputes/<int:dispute_id>/resolve", methods=["POST"])
@jwt_required()
@role_required("admin")
def resolve_conflict(dispute_id):
    json_data = request.get_json() or {}
    data = cast(ResolveDisputeData, resolve_schema.load(json_data))
    
    dispute = process_dispute_resolution(dispute_id, data)
    return jsonify({
        "message": "Conflict resolved and escrow tracking updated.",
        "dispute": dispute_output_schema.dump(dispute.to_dict()),
    }), 200
