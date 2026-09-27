from typing import Literal, TypedDict

from marshmallow import Schema, fields, validate


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

class ResolveDisputeData(TypedDict):
    resolution_status: Literal["released_to_fundi", "refunded"]
    resolution_details: str