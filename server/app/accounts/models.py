from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import ForeignKeyConstraint
from app.extensions import db
import bcrypt 

class User(db.Model):
    __tablename__ = "users"
  
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="customer") # customer, artisan, admin
    is_blocked = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
        
    artisan_profile = db.relationship(
        "ArtisanProfile", backref="user", uselist=False, cascade="all, delete-orphan", lazy="joined"
    )
    
    def set_password(self, plain: str):
        rounds = 10
        self.password_hash = bcrypt.hashpw(
            plain.encode("utf-8"), bcrypt.gensalt(rounds)
        ).decode("utf-8")
        
    def check_password(self, plain: str) -> bool:
        return bcrypt.checkpw(
            plain.encode("utf-8"), self.password_hash.encode("utf-8")
        )
        
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "role": self.role,
            "is_blocked": self.is_blocked,
            "created_at": self.created_at.isoformat(),
        }
        
    def __repr__(self):
        return f"<User {self.name}>"
    
class ArtisanProfile(db.Model):
    __tablename__ = "artisan_profiles"
    __table_args__ = (
        ForeignKeyConstraint(
            ["county_id", "sub_county_id"],
            ["sub_counties.county_id", "sub_counties.id"],
            name="fk_artisan_profiles_county_sub_county",
            ondelete="RESTRICT",
        ),
    )
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    bio = db.Column(db.Text, nullable=True)
    experience_years = db.Column(db.Integer, default=0, nullable=False)
    primary_phone = db.Column(db.String(20), nullable=False)
    profile_image = db.Column(db.String(255), nullable=True)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)

    county_id = db.Column(db.Integer, db.ForeignKey("counties.id", ondelete="RESTRICT"), nullable=False)
    sub_county_id = db.Column(db.Integer, db.ForeignKey("sub_counties.id", ondelete="RESTRICT"), nullable=False)
    specific_address = db.Column(db.String(255), nullable=False) # e.g., "Fedha Estate gate B" 
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "bio": self.bio,
            "experience_years": self.experience_years,
            "primary_phone": self.primary_phone,
            "profile_image": self.profile_image,
            "is_verified": self.is_verified
        }
        
    def __repr__(self):
        return f"<Artisan {self.id}>"