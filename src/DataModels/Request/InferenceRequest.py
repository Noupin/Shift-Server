#pylint: disable=C0103, C0301
"""
The Inference Request Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from marshmallow_dataclass import dataclass


@dataclass(frozen=True)
class InferenceRequest:
    shiftUUID: str
    usePTM: bool = False
    prebuiltShiftModel: str = ""

InferenceRequestDescription = """
The uuid of the shift model being inferenced with, \
whether or not to use the pre trained model(PTM), \
and if using a prebuilt shift model the uuid of that shift.
"""
