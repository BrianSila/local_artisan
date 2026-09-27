from collections.abc import Mapping
from uuid import UUID
from app.extensions import db
from .models import User
from app.common.errors import ForbiddenError, NotFoundError, ValidationError

def get_user_or_404(user_id: UUID | str) -> User:
    try:
        user_uuid = user_id if isinstance(user_id, UUID) else UUID(user_id)
    except (AttributeError, TypeError, ValueError):
        raise NotFoundError("User not found") from None

    user = db.session.get(User, user_uuid)
    if not user:
        raise NotFoundError("User not found")
    return user

def update_profile(user: User, data: Mapping[str, object]) -> User:
    if "name" in data and isinstance(data["name"], str) and data["name"]:
        user.name = data["name"]
    if "phone" in data and isinstance(data["phone"], str):
        user.phone = data["phone"]
    from app.extensions import db
    
    db.session.commit()
    return user

def change_role(actor: User, target_id: UUID | str, new_role: str) -> User:
    if actor.role != "admin":
        raise ForbiddenError("Only admins can change roles")
    target = get_user_or_404(target_id)
    target.role = new_role
    from app.extensions import db
    
    db.session.commit()
    return target

def list_users() -> list:
    users = User.query.order_by(User.created_at.desc()).all()
    return [user.to_dict() for user in users]

def change_password(user: User, password_data: dict) -> bool:
    old_password = password_data.get("old_password")
    new_password = password_data.get("new_password")
    
    if not old_password or not new_password:
        raise ValidationError("both old and new passwords are required")
    
    if not user.check_password(old_password):
        raise ValidationError("The current password you entered is incorrect")
    
    if len(new_password) < 6:
        raise ValidationError("New password must be at least 6 characters long")
    
    user.set_password(new_password)
    
    from app.extensions import db
    
    db.session.commit()
    return True

def deactivate_user_account(user: User) -> User:
    user.is_blocked = True
    db.session.commit()
    return user