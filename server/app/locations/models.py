from sqlalchemy import UniqueConstraint
from app.extensions import db

class County(db.Model):
    __tablename__ = "counties"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False) 
    code = db.Column(db.Integer, unique=True, nullable=False)  
    
    sub_counties = db.relationship("SubCounty", backref="county", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code
        }
        
    def __repr__(self):
        return f"<County {self.id}-{self.name}-{self.code}>"
    
class SubCounty(db.Model):
    __tablename__ = "sub_counties"
    __table_args__ = (
        UniqueConstraint("county_id", "id", name="uq_sub_counties_county_id_id"),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    county_id = db.Column(db.Integer, db.ForeignKey("counties.id", ondelete="CASCADE"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    
    def to_dict(self):
        return {
            "id": self.id,
            "county_id": self.county_id,
            "name": self.name
        }
        
    def __repr__(self):
        return f"<Sub county {self.id}-{self.county_id}-{self.name}>"