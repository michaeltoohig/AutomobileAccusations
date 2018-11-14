# -*- coding: utf-8 -*-

# Import standard library packages

# Import installed packages
from marshmallow import fields

# Import app code
from .base import BaseSchema


class AccusationSchema(BaseSchema):
    # Own properties
    public_id = fields.Str()
    created_at = fields.DateTime()
    comment = fields.Str()
    occured_at = fields.DateTime()
    vehicle = fields.Nested("VehicleSchema", only=("plate"))
    acc_type = fields.Nested("AccusationTypeSchema", only=("name"))
    user = fields.Nested("UserSchema", only=("id"))


class AccusationTypeSchema(BaseSchema):
	# Own properties
	id = fields.Int()
	name = fields.Str()
	desc = fields.Str()
	accusations = fields.Nested(
		"AccusationSchema", 
		only=("public_id", "occured_at", "vehicle"),
		many=True
	)