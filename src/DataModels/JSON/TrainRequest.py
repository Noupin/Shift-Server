#pylint: disable=C0103, C0301
"""
The Train Request Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from marshmallow_dataclass import dataclass


@dataclass(frozen=True)
class TrainRequest:
    shiftUUID: str
    shiftTitle: str
    usePTM: bool
    prebuiltShiftModel: str
    statusInterval: int
    trainType: str
