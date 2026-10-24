from typing import cast
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required, create_access_token
from sqlalchemy import or_
from .schemas import (
    LoginUserData,
    LoginUserSchema,
    RegisterUserData,
    RegisterUserSchema,
    UpdateProfileData,
    UpdateProfileSchema,
    UpdateRoleData,
    UpdateRoleSchema,
    UserSummarySchema,
)
from .services import update_profile, change_role, get_user_or_404, change_password, deactivate_user_account
from app.common.decorators import login_required, role_required
from app.common.errors import ForbiddenError, ConflictError, UnauthorizedError 
from app.common.pagination import paginate
from app.extensions import db  
from app.accounts.models import User

auth_bp = Blueprint("auth", __name__)

register_schema = RegisterUserSchema()
login_schema = LoginUserSchema()
update_schema = UpdateProfileSchema()
role_update_schema = UpdateRoleSchema()
user_summary_schema = UserSummarySchema()

@auth_bp.route("/register", methods=["POST"])
def register():
    json_data = request.get_json() or {}
    
    data = cast(RegisterUserData, register_schema.load(json_data))
    
    if User.query.filter_by(email=data["email"]).first():
        raise ConflictError("Email is already registered")
        
    new_user = User()
    new_user.name = data["name"]
    new_user.email = data["email"]
    new_user.phone = data.get("phone")
    new_user.role = data.get("role", "customer")
    new_user.set_password(data["password"])
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": "User registered successfully", "user": new_user.to_dict()}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    json_data = request.get_json() or {}
    data = cast(LoginUserData, login_schema.load(json_data))
    
    user = User.query.filter_by(email=data["email"]).first()
    
    if not user or not user.check_password(data["password"]):
        raise UnauthorizedError("Invalid email or password")
        
    if user.is_blocked:
        raise ForbiddenError("Account has been suspended by an administrator.")
        
    access_token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
    
    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "user": user.to_dict()
    }), 200

@auth_bp.route("/profile", methods=["PUT"])
@jwt_required()
@login_required  
def handle_profile_update():
    json_data = request.get_json() or {}
    data = cast(UpdateProfileData, update_schema.load(json_data))
    
    current_user_id = get_jwt_identity()
    user = get_user_or_404(current_user_id)
    
    updated_user = update_profile(user, data)
    return jsonify({"message": "Profile updated successfully", "user": updated_user.to_dict()}), 200

@auth_bp.route("/change-password", methods=["POST"])
@jwt_required()
@login_required
def handle_password_change():
    json_data = request.get_json() or {}
    current_user_id = get_jwt_identity()
    user = get_user_or_404(current_user_id)
    
    change_password(user, json_data)
    return jsonify({"message": "Password changed successfully."}), 200

@auth_bp.route("/deactivate", methods=["POST"])
@jwt_required()
@login_required
def handle_deactivation():
    current_user_id = get_jwt_identity()
    user = get_user_or_404(current_user_id)
    
    deactivate_user_account(user)
    return jsonify({"message": "Account successfully deactivated."}), 200

@auth_bp.route("/users", methods=["GET"])
@jwt_required()
@role_required("admin")  
def get_all_users():
    query = User.query
    search = request.args.get("q", "", type=str).strip()
    if search:
        term = f"%{search}%"
        query = query.filter(or_(User.name.ilike(term), User.email.ilike(term), User.phone.ilike(term)))
    role = request.args.get("role", "", type=str).strip()
    if role in {"customer", "artisan", "admin"}:
        query = query.filter(User.role == role)
    status = request.args.get("status", "", type=str).strip()
    if status == "active":
        query = query.filter(User.is_blocked.is_(False))
    elif status == "suspended":
        query = query.filter(User.is_blocked.is_(True))
    sort = request.args.get("sort", "default", type=str)
    query = query.order_by(User.name.asc() if sort == "name_asc" else User.created_at.desc())
    
    paginated_users = paginate(query=query, schema=user_summary_schema)
    return jsonify(paginated_users), 200

@auth_bp.route("/users/<string:user_id>/role", methods=["PATCH"])
@jwt_required()
@role_required("admin")
def handle_role_change(user_id):
    json_data = request.get_json() or {}
    data = cast(UpdateRoleData, role_update_schema.load(json_data))
    
    current_user_id = get_jwt_identity()
    actor = get_user_or_404(current_user_id)
    
    updated_target = change_role(actor, user_id, data["role"])
    return jsonify({"message": "User role updated successfully", "user": updated_target.to_dict()}), 200
