#pylint: disable=C0103, C0301
"""
The User Shifts Request Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from marshmallow_dataclass import dataclass

#First Party Imports
from src.DataModels.Request.BasePaginationRequest import BasePaginationRequest


@dataclass(frozen=True)
class UserShiftsRequest(BasePaginationRequest):
    pass

UserShiftsRequestDescription = """The page of user shifts to get."""
