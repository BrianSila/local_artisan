from typing import cast
from flask import Blueprint, request, jsonify, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.accounts.models import User
from app.artisan.schemas import (
    OnboardArtisanData,
    OnboardArtisanSchema,
    ProfileImageUploadData,
    ProfileImageUploadSchema,
)
from app.services.schemas import ServiceCatalogSchema
from app.artisan.services import (
    onboard_artisan_account,
    update_artisan_bio,
    update_artisan_profile_image,
)
from app.services.services import add_catalog_service, remove_catalog_service
from app.common.decorators import login_required, role_required
from app.common.errors import NotFoundError
from app.common.utilis import coerce_form

artisan_bp = Blueprint("artisan", __name__)

onboard_schema = OnboardArtisanSchema()
profile_image_schema = ProfileImageUploadSchema()
catalog_schema = ServiceCatalogSchema()

@artisan_bp.route("/onboard", methods=["POST"])
@jwt_required()
def onboard():
    if request.is_json:
        json_data = request.get_json() or {}
    else:
        json_data = coerce_form(request.form.to_dict())
        image_file = request.files.get("profile_image")
        if image_file is not None:
            json_data["profile_image"] = image_file
    data = cast(OnboardArtisanData, onboard_schema.load(json_data))
    
    current_user_id = get_jwt_identity()
    profile = onboard_artisan_account(
        current_user_id,
        data,
        profile_image=data.get("profile_image"),
    )
    return jsonify({"message": "Artisan account onboarded successfully", "profile": profile.to_dict()}), 201


@artisan_bp.route("/profile/image", methods=["PUT"])
@jwt_required()
@role_required("artisan")
def update_profile_image():
    current_user_id = get_jwt_identity()
    data = cast(
        ProfileImageUploadData,
        profile_image_schema.load({"profile_image": request.files.get("profile_image")}),
    )
    profile = update_artisan_profile_image(
        current_user_id,
        data["profile_image"],
    )
    image_url = url_for("static", filename=profile.profile_image)
    return jsonify({"message": "Profile image updated successfully", "profile_image_url": image_url}), 200

@artisan_bp.route("/profile", methods=["PUT"])
@jwt_required()
@role_required("artisan")
def update_profile():
    json_data = request.get_json() or {}
    current_user_id = get_jwt_identity()
    
    updated_profile = update_artisan_bio(current_user_id, json_data)
    return jsonify({"message": "Profile updated successfully", "profile": updated_profile.to_dict()}), 200

@artisan_bp.route("/services", methods=["POST"])
@jwt_required()
@role_required("artisan")
def add_service():
    json_data = request.get_json() or {}
    data = cast(dict, catalog_schema.load(json_data))
    
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if user is None or user.artisan_profile is None:
        raise NotFoundError("Artisan profile not found")
    
    service = add_catalog_service(user.artisan_profile.id, data)
    return jsonify({"message": "Service added to catalog", "service": service.to_dict()}), 201

@artisan_bp.route("/services/<string:service_id>", methods=["DELETE"])
@jwt_required()
@role_required("artisan")
def delete_service(service_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if user is None or user.artisan_profile is None:
        raise NotFoundError("Artisan profile not found")
    
    remove_catalog_service(user.artisan_profile.id, service_id)
    return jsonify({"message": "Service successfully removed from catalog"}), 200
