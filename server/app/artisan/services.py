from uuid import UUID
from typing import cast
from werkzeug.datastructures import FileStorage
from app.extensions import db
from app.accounts.models import ArtisanProfile, User
from app.common.errors import NotFoundError, ValidationError
from app.common.uploads import delete_image, save_image
from app.artisan.schemas import OnboardArtisanData


def onboard_artisan_account(
    user_id: UUID | str,
    data: OnboardArtisanData,
    profile_image: FileStorage | None = None,
) -> ArtisanProfile:
    try:
        user_uuid = UUID(str(user_id))
    except (AttributeError, TypeError, ValueError):
        raise NotFoundError("User account not found") from None

    user = db.session.get(User, user_uuid)
    if not user:
        raise NotFoundError("User account not found")
    if user.artisan_profile:
        raise ValidationError("An artisan profile is already active on this account")

    profile = ArtisanProfile()
    profile.user_id = user.id
    profile.bio = data["bio"]
    profile.experience_years = data["experience_years"]
    profile.primary_phone = data["primary_phone"]
    profile.county_id = data["county_id"]
    profile.sub_county_id = data["sub_county_id"]
    profile.specific_address = data["specific_address"]
    profile.latitude = data.get("latitude")
    profile.longitude = data.get("longitude")
    image_path = save_image(profile_image) if profile_image else None
    profile.profile_image = image_path
    user.role = "artisan"
    
    db.session.add(profile)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        if image_path:
            delete_image(image_path)
        raise
    return profile


def update_artisan_profile_image(user_id: UUID | str, image_file: FileStorage) -> ArtisanProfile:
    try:
        user_uuid = UUID(str(user_id))
    except (AttributeError, TypeError, ValueError):
        raise NotFoundError("Artisan profile not found") from None

    user = db.session.get(User, user_uuid)
    if user is None or user.artisan_profile is None:
        raise NotFoundError("Artisan profile not found")

    profile = cast(ArtisanProfile, user.artisan_profile)
    new_path = save_image(image_file)
    old_path = profile.profile_image
    profile.profile_image = new_path
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        delete_image(new_path)
        raise

    if old_path:
        delete_image(old_path)
    return profile

def update_artisan_bio(user_id: str, data: dict) -> ArtisanProfile:
    user = User.query.get(user_id)
    if not user or not user.artisan_profile:
        raise NotFoundError("Artisan profile not found")
        
    profile = user.artisan_profile
    if "bio" in data: profile.bio = data["bio"]
    if "primary_phone" in data: profile.primary_phone = data["primary_phone"]
    if "specific_address" in data: profile.specific_address = data["specific_address"]
    if "latitude" in data: profile.latitude = data["latitude"]
    if "longitude" in data: profile.longitude = data["longitude"]
    
    db.session.commit()
    return profile

