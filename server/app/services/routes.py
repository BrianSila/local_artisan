from typing import Any, cast
from uuid import UUID
from flask import Blueprint, request, jsonify, url_for
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.extensions import cache, db
from app.accounts.models import ArtisanProfile, SavedArtisan
from app.services.models import Category, ArtisanService
from app.services.schemas import CategorySchema, ArtisanServiceSchema, PublicReviewSchema, SaveArtisanSchema, WhatsAppContactSchema
from app.services.schemas import (
    CategorySchema,
    ArtisanServiceSchema,
    WhatsAppContactData,
    WhatsAppContactSchema,
)
from app.services.services import build_filtered_services_query, distance_km_expression, get_artisan_public_stats
from app.bookings.models import AvailabilitySlot
from app.bookings.schemas import AvailabilitySlotSchema
from app.operations.models import Review
from app.common.pagination import paginate
from app.common.decorators import login_required, role_required
from app.common.errors import APIError, NotFoundError
from app.common.validators import whatsapp_link

services_bp = Blueprint("services_public", __name__)

category_list_schema = CategorySchema(many=True)
service_schema = ArtisanServiceSchema()
availability_schema = AvailabilitySlotSchema(many=True)
public_review_schema = PublicReviewSchema(many=True)
save_artisan_schema = SaveArtisanSchema()
whatsapp_contact_schema = WhatsAppContactSchema()


def _attach_artisan_stats(items):
    stats = get_artisan_public_stats(item["artisan_id"] for item in items)
    for item in items:
        item.update(stats[item["artisan_id"]])


def _public_artisan_summary(profile):
    stats = get_artisan_public_stats([profile.id])[str(profile.id)]
    return {
        "id": str(profile.id),
        "name": profile.user.name,
        "profile_image_url": (
            url_for("static", filename=profile.profile_image, _external=True)
            if profile.profile_image else None
        ),
        "bio": profile.bio,
        "experience_years": profile.experience_years,
        "is_verified": profile.is_verified,
        "county_name": profile.county.name,
        "sub_county_name": profile.sub_county.name,
        **stats,
    }

@services_bp.route("/categories", methods=["GET"])
@cache.cached(timeout=86400)
def get_public_categories():
    categories = Category.query.order_by(Category.name).all()
    return jsonify(category_list_schema.dump(categories)), 200

@services_bp.route("/search", methods=["GET"])
def search_marketplace_listings():
    raw_latitude = request.args.get("latitude")
    raw_longitude = request.args.get("longitude")
    raw_radius = request.args.get("radius_km")
    if (raw_latitude is None) != (raw_longitude is None):
        raise APIError("Latitude and longitude must be provided together.")

    latitude = request.args.get("latitude", type=float)
    longitude = request.args.get("longitude", type=float)
    try:
        radius_km = float(raw_radius) if raw_radius is not None else 10.0
    except ValueError:
        raise APIError("Radius must be a valid number.") from None
    if raw_latitude is not None and (latitude is None or longitude is None):
        raise APIError("Latitude and longitude must be valid numbers.")
    if latitude is not None and not -90 <= latitude <= 90:
        raise APIError("Latitude must be between -90 and 90.")
    if longitude is not None and not -180 <= longitude <= 180:
        raise APIError("Longitude must be between -180 and 180.")
    if raw_radius is not None and radius_km is None:
        raise APIError("Radius must be a valid number.")
    if not 0 < radius_km <= 500:
        raise APIError("Radius must be greater than 0 and no more than 500 km.")
    if raw_radius is not None and latitude is None:
        raise APIError("A radius search requires latitude and longitude.")

    filters = {
        "category_slug": request.args.get("category_slug"),
        "county_id": request.args.get("county_id", type=int),
        "sub_county_id": request.args.get("sub_county_id", type=int),
        "search_term": request.args.get("search_term"),
        "latitude": latitude,
        "longitude": longitude,
        "radius_km": radius_km,
    }
    query_stmt = build_filtered_services_query(filters)

    if latitude is not None and longitude is not None:
        page = request.args.get("page", 1, type=int)
        limit = min(request.args.get("limit", 20, type=int), 100)
        distance = distance_km_expression(latitude, longitude)
        query_with_distance = cast(Any, query_stmt.add_columns(distance.label("distance_km")))
        pagination = query_with_distance.paginate(page=page, per_page=limit, error_out=False)
        items = []
        for service, distance_km in pagination.items:
            item = cast(dict[str, Any], service_schema.dump(service))
            item["distance_km"] = round(float(distance_km), 2)
            items.append(item)
        paginated_results = {
            "total": pagination.total,
            "page": pagination.page,
            "pages": pagination.pages,
            "items": items,
        }
    else:
        paginated_results = paginate(query=query_stmt, schema=service_schema)

    _attach_artisan_stats(paginated_results["items"])
    
    return jsonify(paginated_results), 200

@services_bp.route("/listings/<uuid:service_id>", methods=["GET"])
def get_specific_listings(service_id):  
    service = db.session.get(ArtisanService, service_id)
    if not service:
        raise NotFoundError("The specified marketplace catalog item does not exist")
        
    item = service_schema.dump(service)
    _attach_artisan_stats([item])
    return jsonify(item), 200


@services_bp.route("/artisans/<uuid:artisan_id>", methods=["GET"])
def get_public_artisan_profile(artisan_id):
    profile = db.session.get(ArtisanProfile, artisan_id)
    if profile is None or not profile.is_verified:
        raise NotFoundError("The specified artisan profile does not exist")

    services = (
        ArtisanService.query.filter_by(artisan_id=profile.id)
        .order_by(ArtisanService.title.asc(), ArtisanService.id.asc())
        .all()
    )
    public_services = [service_schema.dump(service) for service in services]
    _attach_artisan_stats(public_services)
    stats = get_artisan_public_stats([profile.id])[str(profile.id)]
    return jsonify({
        "id": str(profile.id),
        "name": profile.user.name,
        "profile_image_url": (
            url_for("static", filename=profile.profile_image, _external=True)
            if profile.profile_image else None
        ),
        "bio": profile.bio,
        "experience_years": profile.experience_years,
        "is_verified": profile.is_verified,
        **stats,
        "county_name": profile.county.name,
        "sub_county_name": profile.sub_county.name,
        "services": public_services,
        "work_photos": [
            url_for("static", filename=photo, _external=True)
            for photo in profile.work_photos
        ],
    }), 200


@services_bp.route("/artisans/<uuid:artisan_id>/reviews", methods=["GET"])
def get_public_artisan_reviews(artisan_id):
    profile = db.session.get(ArtisanProfile, artisan_id)
    if profile is None or not profile.is_verified:
        raise NotFoundError("The specified artisan profile does not exist")
    reviews = Review.query.filter_by(artisan_id=artisan_id).order_by(
        Review.created_at.desc(), Review.id.desc()
    )
    return jsonify(paginate(query=reviews, schema=public_review_schema)), 200


@services_bp.route("/saved-artisans", methods=["GET"])
@jwt_required()
@login_required
@role_required("customer")
def list_saved_artisans():
    customer_id = UUID(str(get_jwt_identity()))
    saved_rows = (
        SavedArtisan.query.join(ArtisanProfile)
        .filter(
            SavedArtisan.customer_id == customer_id,
            ArtisanProfile.is_verified.is_(True),
        )
        .order_by(SavedArtisan.created_at.desc(), SavedArtisan.id.desc())
        .all()
    )
    return jsonify([
        {
            "saved_at": saved.created_at.isoformat(),
            "artisan": _public_artisan_summary(saved.artisan_profile),
        }
        for saved in saved_rows
    ]), 200


@services_bp.route("/saved-artisans", methods=["POST"])
@jwt_required()
@login_required
@role_required("customer")
def save_artisan():
    data = save_artisan_schema.load(request.get_json() or {})
    profile = db.session.get(ArtisanProfile, data["artisan_id"])
    if profile is None or not profile.is_verified:
        raise NotFoundError("The specified artisan profile does not exist")

    customer_id = UUID(str(get_jwt_identity()))
    saved = SavedArtisan.query.filter_by(
        customer_id=customer_id,
        artisan_id=profile.id,
    ).first()
    if saved is None:
        saved = SavedArtisan(customer_id=customer_id, artisan_id=profile.id)
        db.session.add(saved)
        db.session.commit()
        status_code = 201
    else:
        status_code = 200
    return jsonify({"saved": True, "artisan": _public_artisan_summary(profile)}), status_code


@services_bp.route("/saved-artisans/<uuid:artisan_id>", methods=["DELETE"])
@jwt_required()
@login_required
@role_required("customer")
def unsave_artisan(artisan_id):
    saved = SavedArtisan.query.filter_by(
        customer_id=UUID(str(get_jwt_identity())),
        artisan_id=artisan_id,
    ).first()
    if saved is None:
        raise NotFoundError("Saved artisan not found")
    db.session.delete(saved)
    db.session.commit()
    return jsonify({"saved": False}), 200


@services_bp.route("/artisans/<uuid:artisan_id>/availability", methods=["GET"])
def get_public_artisan_availability(artisan_id):
    profile = db.session.get(ArtisanProfile, artisan_id)
    if profile is None or not profile.is_verified:
        raise NotFoundError("The specified artisan profile does not exist")

    slots = (
        AvailabilitySlot.query.filter(
            AvailabilitySlot.artisan_id == artisan_id,
            AvailabilitySlot.status == "available",
            AvailabilitySlot.starts_at > db.func.now(),
        )
        .order_by(AvailabilitySlot.starts_at.asc())
        .all()
    )
    return jsonify(availability_schema.dump(slots)), 200


@services_bp.route("/listings/<uuid:service_id>/whatsapp", methods=["GET"])
@jwt_required()
@login_required
def get_whatsapp_contact_link(service_id):
    service = db.session.get(ArtisanService, service_id)
    if service is None:
        raise NotFoundError("The specified marketplace catalog item does not exist")

    artisan = db.session.get(ArtisanProfile, service.artisan_id)
    if artisan is None or not artisan.is_verified:
        raise NotFoundError("The artisan is not available for contact")

    data = cast(WhatsAppContactData, whatsapp_contact_schema.load(request.args.to_dict()))
    try:
        link = whatsapp_link(artisan.primary_phone, data["message"])
    except ValueError as error:
        raise APIError(str(error), status_code=400) from None

    return jsonify({"whatsapp_url": link}), 200