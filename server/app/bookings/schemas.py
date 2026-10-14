from marshmallow import Schema, fields, validate, validates, ValidationError
from flask import url_for
import datetime
from typing import Literal, NotRequired, TypedDict
from uuid import UUID


class CreateBookingData(TypedDict):
    artisan_id: UUID
    service_id: UUID
    availability_slot_id: int
    scheduled_date: NotRequired[datetime.datetime]
    notes: NotRequired[str]


class UpdateBookingStatusData(TypedDict):
    status: Literal["accepted", "dispatched", "completed", "cancelled"]


class BookingResponseSchema(Schema):
    id = fields.UUID(dump_only=True)
    scheduled_date = fields.DateTime(dump_only=True)
    status = fields.Str(dump_only=True)
    notes = fields.Str(allow_none=True, dump_only=True)
    customer_id = fields.UUID(dump_only=True)
    artisan_id = fields.UUID(dump_only=True)
    service_id = fields.UUID(allow_none=True, dump_only=True)
    availability_slot_id = fields.Int(allow_none=True, dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    service_title = fields.Method("get_service_title", dump_only=True)
    service_description = fields.Method("get_service_description", dump_only=True)
    service_price_type = fields.Method("get_service_price_type", dump_only=True)
    service_base_price = fields.Method("get_service_base_price", dump_only=True)
    artisan_name = fields.Method("get_artisan_name", dump_only=True)
    artisan_phone = fields.Method("get_artisan_phone", dump_only=True)
    artisan_photo_url = fields.Method("get_artisan_photo_url", dump_only=True)
    customer_name = fields.Method("get_customer_name", dump_only=True)
    customer_phone = fields.Method("get_customer_phone", dump_only=True)
    allowed_actions = fields.List(fields.Str(), dump_only=True)

    def get_service_title(self, booking):
        return booking.service.title if booking.service else None

    def get_service_description(self, booking):
        return booking.service.description if booking.service else None

    def get_service_price_type(self, booking):
        return booking.service.price_type if booking.service else None

    def get_service_base_price(self, booking):
        return float(booking.service.base_price) if booking.service else None

    def get_artisan_name(self, booking):
        return booking.artisan_profile.user.name if booking.artisan_profile else None

    def get_artisan_phone(self, booking):
        return booking.artisan_profile.primary_phone if booking.artisan_profile else None

    def get_artisan_photo_url(self, booking):
        profile_image = booking.artisan_profile.profile_image if booking.artisan_profile else None
        return url_for("static", filename=profile_image, _external=True) if profile_image else None

    def get_customer_name(self, booking):
        return booking.customer.name if booking.customer else None

    def get_customer_phone(self, booking):
        return booking.customer.phone if booking.customer else None

class CreateBookingSchema(Schema):
    artisan_id = fields.UUID(required=True)
    service_id = fields.UUID(required=True)
    availability_slot_id = fields.Int(required=True)
    scheduled_date = fields.DateTime(required=False)
    notes = fields.Str(required=False, validate=validate.Length(max=500))


class CreateAvailabilitySlotData(TypedDict):
    starts_at: datetime.datetime
    ends_at: datetime.datetime


class CreateAvailabilitySlotSchema(Schema):
    starts_at = fields.DateTime(required=True)
    ends_at = fields.DateTime(required=True)


class AvailabilitySlotSchema(Schema):
    id = fields.Int(dump_only=True)
    artisan_id = fields.UUID(dump_only=True)
    starts_at = fields.DateTime(dump_only=True)
    ends_at = fields.DateTime(dump_only=True)
    status = fields.Str(dump_only=True)

class UpdateBookingStatusSchema(Schema):
    status = fields.Str(required=True, validate=validate.OneOf(
        ["accepted", "dispatched", "completed", "cancelled"]
    ))
