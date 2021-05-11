#pylint: disable=C0103, C0301
"""
The New Shifts Response Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from marshmallow import Schema, fields

#First Party Imports
from src.DataModels.Marshmallow.Shift import ShiftSchema


class NewShiftsResponse(Schema):
    shifts = fields.List(fields.Nested(ShiftSchema))

NewShiftsResponseDescription = """The newest shifts."""
