#pylint: disable=C0103, C0301
"""
The Popular Shifts Response Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from marshmallow import Schema, fields

#First Party Imports
from src.constants import AMOUNT_OF_POPULAR
from src.models.Marshmallow.Shift import ShiftSchema


class PopularShiftsResponse(Schema):
    shifts = fields.List(fields.Nested(ShiftSchema))

PopularShiftsResponseDescription = f"""The top {AMOUNT_OF_POPULAR} most popular shifts."""
