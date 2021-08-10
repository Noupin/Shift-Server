#pylint: disable=C0103, C0301
"""
The Shift Category Request Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from marshmallow_dataclass import dataclass

#First Party Imports
from src.models.Request.BasePaginationRequest import BasePaginationRequest


@dataclass(frozen=True)
class ShiftCategoryRequest(BasePaginationRequest):
    pass

ShiftCategoryRequestDescription = """The page of shifts to get from the chosen category."""
