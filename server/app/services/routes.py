from typing import cast
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.extensions import cache, db
from app.accounts.models import ArtisanProfile
from app.services.models import Category, ArtisanService
from app.services.schemas import CategorySchema, ArtisanServiceSchema, WhatsAppContactSchema
from app.services.schemas import (
    CategorySchema,
    ArtisanServiceSchema,
    WhatsAppContactData,
    WhatsAppContactSchema,
)
from app.services.services import build_filtered_services_query
from app.common.pagination import paginate
from app.common.decorators import login_required
from app.common.errors import APIError, NotFoundError
from app.common.validators import whatsapp_link

services_bp = Blueprint("services_public", __name__)

category_list_schema = CategorySchema(many=True)
service_schema = ArtisanServiceSchema()
whatsapp_contact_schema = WhatsAppContactSchema()

@services_bp.route("/categories", methods=["GET"])
@cache.cached(timeout=86400)
def get_public_categories():
    categories = Category.query.order_by(Category.name).all()
    return jsonify(category_list_schema.dump(categories)), 200

@services_bp.route("/search", methods=["GET"])
def search_marketplace_listings():
    filters = {
        "category_slug": request.args.get("category_slug"),
        "county_id": request.args.get("county_id", type=int),
        "sub_county_id": request.args.get("sub_county_id", type=int),
        "search_term": request.args.get("search_term")
    }
    query_stmt = build_filtered_services_query(filters)
    
    paginated_results = paginate(query=query_stmt, schema=service_schema)
    
    return jsonify(paginated_results), 200

@services_bp.route("/listings/<uuid:service_id>", methods=["GET"])
def get_specific_listings(service_id):  
    service = db.session.get(ArtisanService, service_id)
    if not service:
        raise NotFoundError("The specified marketplace catalog item does not exist")
        
    return jsonify(service.to_dict()), 200


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