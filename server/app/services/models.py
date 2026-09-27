import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import CheckConstraint
from app.extensions import db

class Category(db.Model):
    __tablename__ = "categories"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False) # e.g., Electrician
    slug = db.Column(db.String(120), unique=True, nullable=False) # e.g., electrical-installations
    icon_name = db.Column(db.String(50), nullable=False)          # Passed to React to render the Lucide icon

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "icon_name": self.icon_name
        }
        
    def __repr__(self):
        return f"<Category {self.id}>"
    
class ArtisanService(db.Model):
    __tablename__ = "artisan_services"
    __table_args__ = (
        CheckConstraint("base_price >= 0", name='ck_artisan_services_base_price_nonnegative'),
        CheckConstraint(
            "price_type IN ('fixed', 'hourly', 'negotiable')",
            name='ck_artisan_services_price_type',
        ),
    )
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = db.Column(db.String(150), nullable=False)             # e.g., "Instant Shower Repair"
    description = db.Column(db.Text, nullable=False)
    price_type = db.Column(db.String(20), nullable=False, default="fixed") # fixed, hourly, negotiable
    base_price = db.Column(db.Numeric(10, 2), nullable=False)     # Ksh
    
    artisan_id = db.Column(UUID(as_uuid=True), db.ForeignKey("artisan_profiles.id", ondelete="CASCADE"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False)
    
    def to_dict(self):
        return {
            "id": self.id,
            "artisan_id": self.artisan_id,
            "category_id": self.category_id,
            "title": self.title,
            "description": self.description,
            "price_type": self.price_type,
            "base_price": float(self.base_price),
        }
        
    def __repr__(self):
        return f"<Service {self.title}>"