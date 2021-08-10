#pylint: disable=C0103, C0301
"""
The User Shifts Response Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from marshmallow import fields, Schema

#First Party Imports
from src.models.Marshmallow.Shift import ShiftSchema


class UserShiftsResponse(Schema):
    shifts = fields.List(fields.Nested(ShiftSchema))

UserShiftsResponseDescription = """The shifts for the user who is logged in."""
