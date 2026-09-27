from typing import NotRequired, TypedDict

from marshmallow import Schema, ValidationError, fields, validate
from werkzeug.datastructures import FileStorage


def validate_profile_image(value: object) -> None:
    if not isinstance(value, FileStorage) or not value.filename:
        raise ValidationError("A profile image file is required.")


class OnboardArtisanData(TypedDict):
    bio: str
    experience_years: int
    primary_phone: str
    county_id: int
    sub_county_id: int
    specific_address: str
    profile_image: NotRequired[FileStorage]


class OnboardArtisanSchema(Schema):
    bio = fields.Str(required=True, validate=validate.Length(min=10, max=1000))
    experience_years = fields.Int(required=True, validate=validate.Range(min=0, max=50))
    primary_phone = fields.Str(required=True, validate=validate.Length(min=10, max=15))
    county_id = fields.Int(required=True)
    sub_county_id = fields.Int(required=True)
    specific_address = fields.Str(required=True, validate=validate.Length(min=2, max=255))
    profile_image = fields.Raw(load_only=True, validate=validate_profile_image)

class ProfileImageUploadData(TypedDict):
    profile_image: FileStorage

class ProfileImageUploadSchema(Schema):
    profile_image = fields.Raw(required=True, load_only=True, validate=validate_profile_image)