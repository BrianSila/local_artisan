from marshmallow import Schema, fields, validate, validates, ValidationError
import datetime
from typing import Literal, NotRequired, TypedDict
from uuid import UUID


class CreateBookingData(TypedDict):
    artisan_id: UUID
    service_id: UUID
    scheduled_date: datetime.datetime
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
    created_at = fields.DateTime(dump_only=True)

class CreateBookingSchema(Schema):
    artisan_id = fields.UUID(required=True)
    service_id = fields.UUID(required=True)
    scheduled_date = fields.DateTime(required=True)
    notes = fields.Str(required=False, validate=validate.Length(max=500))

    @validates("scheduled_date")
    def validate_future_date(self, value):
        if value < datetime.datetime.utcnow():
            raise ValidationError("Appointment scheduling date must be set in the future.")

class UpdateBookingStatusSchema(Schema):
    status = fields.Str(required=True, validate=validate.OneOf(
        ["accepted", "dispatched", "completed", "cancelled"]
    ))
