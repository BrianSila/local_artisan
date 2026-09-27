from typing import Literal, NotRequired, TypedDict
from marshmallow import Schema, fields, validate

class RegisterUserSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6, max=50))
    phone = fields.Str(required=False)
    role = fields.Str(required=False, validate=validate.OneOf(["customer", "artisan"]))

class RegisterUserData(TypedDict):
    name: str
    email: str
    password: str
    phone: NotRequired[str]
    role: NotRequired[Literal["customer", "artisan"]]
    
class LoginUserSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)
    
class LoginUserData(TypedDict):
    email: str
    password: str

class UpdateProfileSchema(Schema):
    name = fields.Str(required=False, validate=validate.Length(min=2, max=100))
    phone = fields.Str(required=False)

class UpdateProfileData(TypedDict, total=False):
    name: str
    phone: str
    
class UpdateRoleSchema(Schema):
    role = fields.Str(required=True, validate=validate.OneOf(["customer", "artisan", "admin"]))

class UpdateRoleData(TypedDict):
    role: Literal["customer", "artisan", "admin"]
    
class UserSummarySchema(Schema):
    id = fields.UUID()
    name = fields.Str()
    email = fields.Email()
    phone = fields.Str(allow_none=True)
    role = fields.Str()
    is_blocked = fields.Bool()
    created_at = fields.DateTime()
