from typing import cast
from uuid import UUID
from pathlib import Path
from flask import Blueprint, request, jsonify, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.accounts.models import User
from app.artisan.schemas import (
    ArtisanProfileUpdateSchema,
    OnboardArtisanData,
    OnboardArtisanSchema,
    ProfileImageUploadData,
    ProfileImageUploadSchema,
)
from app.services.schemas import ServiceCatalogSchema
from app.services.models import ArtisanService
from app.services.schemas import ArtisanServiceSchema
from app.artisan.services import (
    onboard_artisan_account,
    update_artisan_bio,
    update_artisan_profile_image,
)
from app.services.services import add_catalog_service, remove_catalog_service
from app.common.decorators import login_required, role_required
from app.common.errors import NotFoundError
from app.common.errors import APIError
from app.common.utilis import coerce_form
from app.common.uploads import delete_image, save_image

artisan_bp = Blueprint("artisan", __name__)

onboard_schema = OnboardArtisanSchema()
profile_image_schema = ProfileImageUploadSchema()
profile_update_schema = ArtisanProfileUpdateSchema()
catalog_schema = ServiceCatalogSchema()
catalog_list_schema = ArtisanServiceSchema(many=True)


@artisan_bp.route("/profile", methods=["GET"])
@jwt_required()
@login_required
@role_required("artisan")
def get_own_profile():
    current_user_id = get_jwt_identity()
    user = db.session.get(User, UUID(str(current_user_id)))
    if user is None or user.artisan_profile is None:
        raise NotFoundError("Artisan profile not found")

    profile = user.artisan_profile
    return jsonify({
        "profile": {
            "id": str(profile.id),
            "user_id": str(profile.user_id),
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "bio": profile.bio,
            "experience_years": profile.experience_years,
            "primary_phone": profile.primary_phone,
            "profile_image_url": (
                url_for("static", filename=profile.profile_image, _external=True)
                if profile.profile_image else None
            ),
            "is_verified": profile.is_verified,
            "county_id": profile.county_id,
            "county_name": profile.county.name,
            "sub_county_id": profile.sub_county_id,
            "sub_county_name": profile.sub_county.name,
            "specific_address": profile.specific_address,
            "latitude": profile.latitude,
            "longitude": profile.longitude,
            "work_photos": [
                url_for("static", filename=photo, _external=True)
                for photo in profile.work_photos
            ],
        }
    }), 200

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
    data = profile_update_schema.load(request.get_json() or {})
    current_user_id = get_jwt_identity()
    
    updated_profile = update_artisan_bio(current_user_id, data)
    return jsonify({"message": "Profile updated successfully", "profile": updated_profile.to_dict()}), 200


@artisan_bp.route("/profile/work-photos", methods=["POST"])
@jwt_required()
@role_required("artisan")
def add_work_photos():
    current_user_id = get_jwt_identity()
    user = db.session.get(User, UUID(str(current_user_id)))
    if user is None or user.artisan_profile is None:
        raise NotFoundError("Artisan profile not found")

    files = [image for image in request.files.getlist("work_photos") if image.filename]
    profile = user.artisan_profile
    if not files:
        raise APIError("At least one work photo is required", status_code=400)
    if len(profile.work_photos) + len(files) > 10:
        raise APIError("An artisan profile can have no more than 10 work photos", status_code=400)

    saved_photos = []
    try:
        for image in files:
            saved_photos.append(save_image(image))
        profile.work_photos = [*profile.work_photos, *saved_photos]
        db.session.commit()
    except Exception:
        db.session.rollback()
        for photo in saved_photos:
            delete_image(photo)
        raise

    return jsonify({
        "message": "Work photos added successfully",
        "work_photos": [
            url_for("static", filename=photo, _external=True)
            for photo in profile.work_photos
        ],
    }), 201


@artisan_bp.route("/profile/work-photos/<string:filename>", methods=["DELETE"])
@jwt_required()
@role_required("artisan")
def delete_work_photo(filename):
    current_user_id = get_jwt_identity()
    user = db.session.get(User, UUID(str(current_user_id)))
    if user is None or user.artisan_profile is None:
        raise NotFoundError("Artisan profile not found")

    profile = user.artisan_profile
    photo_path = next(
        (photo for photo in profile.work_photos if Path(photo).name == filename),
        None,
    )
    if photo_path is None:
        raise NotFoundError("Work photo not found")

    profile.work_photos = [photo for photo in profile.work_photos if photo != photo_path]
    db.session.commit()
    delete_image(photo_path)
    return jsonify({"message": "Work photo deleted successfully"}), 200

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

@artisan_bp.route("/services", methods=["GET"])
@jwt_required()
@role_required("artisan")
def list_services():
    current_user_id = get_jwt_identity()
    user = db.session.get(User, UUID(str(current_user_id)))
    if user is None or user.artisan_profile is None:
        raise NotFoundError("Artisan profile not found")

    services = (
        ArtisanService.query.filter_by(artisan_id=user.artisan_profile.id)
        .order_by(ArtisanService.title.asc(), ArtisanService.id.asc())
        .all()
    )
    return jsonify(catalog_list_schema.dump(services)), 200

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
