#pylint: disable=C0103, C0301
"""
The Inference Request Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from dataclasses import dataclass


@dataclass(frozen=True)
class InferenceRequest:
    shiftUUID: str
    usePTM: bool
    prebuiltShiftModel: str
