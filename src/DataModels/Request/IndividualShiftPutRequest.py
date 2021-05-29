#pylint: disable=C0103, C0301
"""
The Individual Shift Put Request Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from marshmallow import Schema, fields

#First Party Imports
from src.DataModels.Marshmallow.Shift import ShiftSchema


class IndividualShiftPutRequest(Schema):
    requestBody = fields.Nested(ShiftSchema)

IndividualShiftPutRequestDescription = """The shift to update/replace the queried shift."""
