from typing import TypedDict
from flask import url_for
from marshmallow import Schema, fields, validate

class CategorySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(dump_only=True)
    slug = fields.Str(dump_only=True)
    icon_name = fields.Str(dump_only=True)

class ArtisanServiceSchema(Schema):
    id = fields.Str(dump_only=True)
    artisan_id = fields.Str(dump_only=True)
    artisan_name = fields.Method("get_artisan_name", dump_only=True)
    artisan_photo_url = fields.Method("get_artisan_photo_url", dump_only=True)
    is_verified = fields.Method("get_is_verified", dump_only=True)
    county_name = fields.Method("get_county_name", dump_only=True)
    sub_county_name = fields.Method("get_sub_county_name", dump_only=True)
    average_rating = fields.Float(allow_none=True, dump_only=True)
    review_count = fields.Int(dump_only=True)
    completed_job_count = fields.Int(dump_only=True)
    category_id = fields.Int(dump_only=True)
    specialty = fields.Method("get_specialty", dump_only=True)
    title = fields.Str(dump_only=True)
    description = fields.Str(dump_only=True)
    price_type = fields.Str(dump_only=True)
    base_price = fields.Float(dump_only=True)

    def get_artisan_name(self, service):
        return service.artisan_profile.user.name

    def get_artisan_photo_url(self, service):
        profile_image = service.artisan_profile.profile_image
        if not profile_image:
            return None
        return url_for("static", filename=profile_image, _external=True)

    def get_is_verified(self, service):
        return service.artisan_profile.is_verified

    def get_county_name(self, service):
        return service.artisan_profile.county.name

    def get_sub_county_name(self, service):
        return service.artisan_profile.sub_county.name

    def get_specialty(self, service):
        return service.category.name

class WhatsAppContactSchema(Schema):
    message = fields.Str(
        load_default="Hi, I am interested in your service.",
        validate=validate.Length(max=1000),
    )

class WhatsAppContactData(TypedDict):
    message: str


class PublicReviewSchema(Schema):
    id = fields.Int(dump_only=True)
    rating = fields.Int(dump_only=True)
    comment = fields.Str(allow_none=True, dump_only=True)
    created_at = fields.DateTime(dump_only=True)


class SaveArtisanSchema(Schema):
    artisan_id = fields.UUID(required=True)
       
class ServiceCatalogSchema(Schema):
    id = fields.Str(dump_only=True)
    category_id = fields.Int(required=True)
    title = fields.Str(required=True, validate=validate.Length(min=3, max=150))
    description = fields.Str(required=True, validate=validate.Length(min=10, max=1000))
    price_type = fields.Str(required=True, validate=validate.OneOf(["fixed", "hourly", "negotiable"]))
    base_price = fields.Decimal(required=True, validate=validate.Range(min=0))

