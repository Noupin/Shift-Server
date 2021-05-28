#pylint: disable=C0103, C0301
"""
The Individual Shift Response Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from marshmallow import Schema, fields

#First Party Imports
from src.DataModels.Marshmallow.Shift import ShiftSchema


class IndividualShiftResponse(Schema):
    shift = fields.Nested(ShiftSchema)

IndividualShiftResponseDescription = f"""The requested shift."""
