#pylint: disable=C0103, C0301
"""
The Train Request Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from dataclasses import dataclass


@dataclass(frozen=True)
class TrainRequest:
    shiftUUID: str
    shiftTitle: str
    usePTM: bool
    prebuiltShiftModel: str
    epochs: int
    trainType: str
