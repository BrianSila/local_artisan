from typing import TypedDict
from marshmallow import Schema, fields, validate

class CategorySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(dump_only=True)
    slug = fields.Str(dump_only=True)
    icon_name = fields.Str(dump_only=True)

class ArtisanServiceSchema(Schema):
    id = fields.Str(dump_only=True)
    artisan_id = fields.Str(dump_only=True)
    category_id = fields.Int(dump_only=True)
    title = fields.Str(dump_only=True)
    description = fields.Str(dump_only=True)
    price_type = fields.Str(dump_only=True)
    base_price = fields.Float(dump_only=True)

class WhatsAppContactSchema(Schema):
    message = fields.Str(
        load_default="Hi, I am interested in your service.",
        validate=validate.Length(max=1000),
    )

class WhatsAppContactData(TypedDict):
    message: str
       
class ServiceCatalogSchema(Schema):
    id = fields.Str(dump_only=True)
    category_id = fields.Int(required=True)
    title = fields.Str(required=True, validate=validate.Length(min=3, max=150))
    description = fields.Str(required=True, validate=validate.Length(min=10, max=1000))
    price_type = fields.Str(required=True, validate=validate.OneOf(["fixed", "hourly", "negotiable"]))
    base_price = fields.Decimal(required=True, validate=validate.Range(min=0))

