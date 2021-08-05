#pylint: disable=C0103, C0301
"""
The Base Pagination Request Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from marshmallow_dataclass import dataclass


@dataclass(frozen=True)
class BasePaginationRequest:
    page: int
