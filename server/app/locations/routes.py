from typing import Any, cast
from flask import Blueprint, jsonify
from app.extensions import cache
from app.locations.models import County, SubCounty
from app.locations.schemas import CountySchema, SubCountySchema
from sqlalchemy.orm import selectinload

locations_bp = Blueprint("locations", __name__)

county_schema = CountySchema(many=True)
subcounty_schema = SubCountySchema(many=True)

@locations_bp.route("/counties", methods=["GET"])
@cache.cached(timeout=86400) # 60 * 60 * 24
def get_counties():
    relationship = cast(Any, County.sub_counties)
    counties = County.query.options(selectinload(relationship)).order_by(County.code).all()
    return jsonify(county_schema.dump(counties)), 200

@locations_bp.route("/counties/<int:county_id>/subcounties", methods=["GET"])
@cache.cached(timeout=86400, query_string=True)
def get_subcounties(county_id):
    sub_counties = SubCounty.query.filter_by(county_id=county_id).order_by(SubCounty.name).all()
    return jsonify(subcounty_schema.dump(sub_counties)), 200