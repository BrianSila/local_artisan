from collections.abc import Mapping
from typing import Any
from uuid import UUID
from sqlalchemy import case, func, or_
from app.extensions import db
from app.services.models import ArtisanService, Category
from app.accounts.models import ArtisanProfile
from app.bookings.models import Booking
from app.common.errors import NotFoundError
from app.operations.models import Review


def distance_km_expression(latitude: float, longitude: float):
    artisan_latitude = func.radians(ArtisanProfile.latitude)
    artisan_longitude = func.radians(ArtisanProfile.longitude)
    search_latitude = func.radians(latitude)
    longitude_delta = artisan_longitude - func.radians(longitude)
    cosine = (
        func.sin(artisan_latitude) * func.sin(search_latitude)
        + func.cos(artisan_latitude) * func.cos(search_latitude) * func.cos(longitude_delta)
    )
    bounded_cosine = case(
        (cosine > 1.0, 1.0),
        (cosine < -1.0, -1.0),
        else_=cosine,
    )
    return 6371.0 * func.acos(bounded_cosine)


def get_artisan_public_stats(artisan_ids):
    profile_ids = {UUID(str(artisan_id)) for artisan_id in artisan_ids}
    stats = {
        str(profile_id): {
            "average_rating": None,
            "review_count": 0,
            "completed_job_count": 0,
        }
        for profile_id in profile_ids
    }
    if not profile_ids:
        return stats

    review_rows = (
        db.session.query(
            Review.artisan_id,
            func.avg(Review.rating),
            func.count(Review.id),
        )
        .filter(Review.artisan_id.in_(profile_ids))
        .group_by(Review.artisan_id)
        .all()
    )
    for artisan_id, average_rating, review_count in review_rows:
        stats[str(artisan_id)].update(
            average_rating=round(float(average_rating), 2),
            review_count=review_count,
        )

    completed_rows = (
        db.session.query(Booking.artisan_id, func.count(Booking.id))
        .filter(
            Booking.artisan_id.in_(profile_ids),
            Booking.status == "completed",
        )
        .group_by(Booking.artisan_id)
        .all()
    )
    for artisan_id, completed_job_count in completed_rows:
        stats[str(artisan_id)]["completed_job_count"] = completed_job_count
    return stats

def build_filtered_services_query(filters: dict):
    query = ArtisanService.query.join(ArtisanProfile).filter(ArtisanProfile.is_verified == True)

    # Filter by category
    if "category_slug" in filters and filters["category_slug"]:
        query = query.join(Category).filter(Category.slug == filters["category_slug"])
        
    # Filter by location
    if "county_id" in filters and filters["county_id"]:
        query = query.filter(ArtisanProfile.county_id == filters["county_id"])
    if "sub_county_id" in filters and filters["sub_county_id"]:
        query = query.filter(ArtisanProfile.sub_county_id == filters["sub_county_id"])

    if filters.get("latitude") is not None and filters.get("longitude") is not None:
        distance = distance_km_expression(filters["latitude"], filters["longitude"])
        query = (
            query.filter(ArtisanProfile.latitude.isnot(None), ArtisanProfile.longitude.isnot(None))
            .filter(distance <= filters["radius_km"])
            .order_by(distance.asc())
        )
        
    # Filter by text search term matching text tokens inside titles and bios
    if "search_term" in filters and filters["search_term"]:
        term = f"%{filters['search_term']}%"
        query = query.filter(
            or_(
                ArtisanService.title.ilike(term),
                ArtisanService.description.ilike(term),
                ArtisanProfile.bio.ilike(term)
            )
        )

    return query

def add_catalog_service(artisan_profile_id: UUID | str, data: Mapping[str, Any]) -> ArtisanService:
	service = ArtisanService()
	service.artisan_id = UUID(str(artisan_profile_id))
	service.category_id = data["category_id"]
	service.title = data["title"]
	service.description = data["description"]
	service.price_type = data["price_type"]
	service.base_price = data["base_price"]

	db.session.add(service)
	db.session.commit()
	return service


def update_catalog_service(
    artisan_profile_id: UUID | str,
    service_id: UUID | str,
    data: Mapping[str, Any],
) -> ArtisanService:
    try:
        artisan_uuid = UUID(str(artisan_profile_id))
        service_uuid = UUID(str(service_id))
    except (AttributeError, TypeError, ValueError):
        raise NotFoundError("Service catalog item not found or unauthorized") from None

    service = ArtisanService.query.filter_by(
        id=service_uuid,
        artisan_id=artisan_uuid,
    ).first()
    if service is None:
        raise NotFoundError("Service catalog item not found or unauthorized")

    service.category_id = data["category_id"]
    service.title = data["title"]
    service.description = data["description"]
    service.price_type = data["price_type"]
    service.base_price = data["base_price"]
    db.session.commit()
    return service


def remove_catalog_service(artisan_profile_id: UUID | str, service_id: UUID | str) -> None:
	try:
		artisan_uuid = UUID(str(artisan_profile_id))
		service_uuid = UUID(str(service_id))
	except (AttributeError, TypeError, ValueError):
		raise NotFoundError("Service catalog item not found or unauthorized") from None

	service = ArtisanService.query.filter_by(
		id=service_uuid,
		artisan_id=artisan_uuid,
	).first()
	if service is None:
		raise NotFoundError("Service catalog item not found or unauthorized")

	db.session.delete(service)
	db.session.commit()
