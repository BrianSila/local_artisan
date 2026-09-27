from collections.abc import Mapping
from typing import Any
from uuid import UUID
from sqlalchemy import or_
from app.extensions import db
from app.services.models import ArtisanService, Category
from app.accounts.models import ArtisanProfile
from app.common.errors import NotFoundError

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
