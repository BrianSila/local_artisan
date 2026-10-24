from typing import Literal, TypedDict
from marshmallow import Schema, fields, validate
from flask import url_for

class VerifyArtisanData(TypedDict):
    is_verified: bool

class SuspendUserData(TypedDict):
    is_blocked: bool

class VerifyArtisanSchema(Schema):
    is_verified = fields.Boolean(required=True)

class SuspendUserSchema(Schema):
    is_blocked = fields.Boolean(required=True)

class ResolveDisputeSchema(Schema):
    # Enforces hard state choices for escrow reconciliation payouts
    resolution_status = fields.Str(required=True, validate=validate.OneOf(["released_to_fundi", "refunded"]))
    resolution_details = fields.Str(required=True, validate=validate.Length(min=10, max=2000))

class DisputeResponseSchema(Schema):
    id = fields.Int()
    booking_id = fields.Str()
    raised_by = fields.Str()
    reason = fields.Str()
    status = fields.Str()
    resolution_details = fields.Str(allow_none=True)
    created_at = fields.Str()

class PendingArtisanSchema(Schema):
    id = fields.Str()
    user_id = fields.Str()
    name = fields.Method("get_name")
    email = fields.Method("get_email")
    primary_phone = fields.Str()
    bio = fields.Str(allow_none=True)
    experience_years = fields.Int()
    county_id = fields.Int()
    sub_county_id = fields.Int()
    specific_address = fields.Str()
    latitude = fields.Float(allow_none=True)
    longitude = fields.Float(allow_none=True)
    profile_image = fields.Str(allow_none=True)
    profile_image_url = fields.Method("get_profile_image_url", allow_none=True)

    def get_name(self, profile):
        return profile.user.name

    def get_email(self, profile):
        return profile.user.email

    def get_profile_image_url(self, profile):
        return url_for("static", filename=profile.profile_image, _external=True) if profile.profile_image else None

class ResolveDisputeData(TypedDict):
    resolution_status: Literal["released_to_fundi", "refunded"]
    resolution_details: str
