#pylint: disable=C0103, C0301
"""
The Individual Shift Put Response Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from marshmallow_dataclass import dataclass

#First Party Imports
from src.DataModels.Response.DefaultResponse import DefaultResponse


@dataclass(frozen=True)
class IndividualShiftPutResponse(DefaultResponse):
    pass

IndividualShiftPutResponseDescription = """The status message pertaing to the update/replace."""
