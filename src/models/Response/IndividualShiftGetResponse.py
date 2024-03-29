#pylint: disable=C0103, C0301
"""
The Individual Shift Get Response Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from marshmallow import fields, Schema

#First Party Imports
from src.models.Marshmallow.Shift import ShiftSchema


class IndividualShiftGetResponse(Schema):
    shift = fields.Nested(ShiftSchema)
    owner = fields.Boolean(required=True)

IndividualShiftGetResponseDescription = f"""The requested shift."""
