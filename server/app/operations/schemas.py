from marshmallow import Schema, fields, validate
from typing import NotRequired, TypedDict


class SubmitReviewSchema(Schema):
    rating = fields.Int(required=True, validate=validate.Range(min=1, max=5))
    comment = fields.Str(required=False, validate=validate.Length(max=1000))

class SubmitReviewData(TypedDict):
    rating: int
    comment: NotRequired[str]

class ReviewResponseSchema(Schema):
    id = fields.Int()
    booking_id = fields.Str()
    artisan_id = fields.Str()
    rating = fields.Int()
    comment = fields.Str(allow_none=True)
    created_at = fields.Str()
    
class FileDisputeSchema(Schema):
    reason = fields.Str(required=True, validate=validate.Length(min=10, max=2000))

class FileDisputeData(TypedDict):
    reason: str

class DisputeResponseSchema(Schema):
    id = fields.Int()
    booking_id = fields.Str()
    raised_by = fields.Str()
    reason = fields.Str()
    status = fields.Str()
    resolution_details = fields.Str(allow_none=True)
    created_at = fields.Str()

class MpesaCheckoutSchema(Schema):
    phone_number = fields.Str(
        required=True,
        validate=(
            validate.Length(min=10, max=15),
            validate.Regexp(r"^\+?[0-9]{10,15}$", error="Enter a valid phone number."),
        ),
    )
    
class MpesaCheckoutData(TypedDict):
    phone_number: str
    
class MpesaCheckoutResponseSchema(Schema):
    merchant_request_id = fields.Str(data_key="MerchantRequestID")
    checkout_request_id = fields.Str(data_key="CheckoutRequestID")
    response_description = fields.Str(data_key="ResponseDescription")

class MpesaCheckoutResponseData(TypedDict):
    merchant_request_id: str
    checkout_request_id: str
    response_description: str

