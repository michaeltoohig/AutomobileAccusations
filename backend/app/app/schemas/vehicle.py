# -*- coding: utf-8 -*-

# Import standard library packages

# Import installed packages
from marshmallow import fields

# Import app code
from .base import BaseSchema


class VehicleSchema(BaseSchema):
    # Own properties
    created_at = fields.DateTime()
    plate = fields.Str()
