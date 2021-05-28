#pylint: disable=C0103, C0301
"""
The Shift Category Response Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from marshmallow import Schema, fields

#First Party Imports
from src.DataModels.Marshmallow.Shift import ShiftSchema


class ShiftCategoryResponse(Schema):
    shifts = fields.List(fields.Nested(ShiftSchema))

ShiftCategoryResponseDescription = """The shifts for the queried category."""
