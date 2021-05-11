#pylint: disable=C0103, C0301
"""
The Featured Shifts Response Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from marshmallow import Schema, fields

#First Party Imports
from src.DataModels.Marshmallow.Shift import ShiftSchema


class FeaturedShiftsResponse(Schema):
    shifts = fields.List(fields.Nested(ShiftSchema))

FeaturedShiftsResponseDescription = """The currently featured shifts."""
