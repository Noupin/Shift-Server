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
    shiftTitle: str = "New Shift"
    usePTM: bool = False
    prebuiltShiftModel: str = ""
    trainType: str = "basic"

TrainRequestDescription = """The uuid of the shift model being inferenced with, \
the title of the shift that is being trained, whether or not the the PTM is being \
used, the uuid of the prebuilt shift model if one is being used, the amount \
of epochs inbetween the training status updates, and the type of trainign to send \
four pictures or one picture for front end."""
