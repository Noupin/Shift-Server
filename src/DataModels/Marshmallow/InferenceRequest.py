#pylint: disable=C0103, C0301
"""
The Inference Request Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from marshmallow import Schema, fields


class InferenceRequest(Schema):
    shiftUUID = fields.String()
    usePTM = fields.Boolean()
    prebuiltShiftModel = fields.String()