#pylint: disable=C0103, C0301
"""
The Individual Shift Delete Response Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from marshmallow import Schema, fields


class IndividualShiftDeleteResponse(Schema):
    msg = fields.String()

IndividualShiftDeleteResponseDescription = f"""Deletes the requested shift."""
