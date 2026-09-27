from marshmallow import Schema, fields

class SubCountySchema(Schema):
    id = fields.Int(dump_only=True)
    county_id = fields.Int(dump_only=True)
    name = fields.Str(dump_only=True)

class CountySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(dump_only=True)
    code = fields.Int(dump_only=True)
    # Allows pulling nested sub-counties directly if needed
    sub_counties = fields.Nested(SubCountySchema, many=True, dump_only=True)