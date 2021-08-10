#pylint: disable=C0103, C0301
"""
The Categories Request Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from marshmallow_dataclass import dataclass

#First Party Imports
from src.models.Request.BasePaginationRequest import BasePaginationRequest


@dataclass(frozen=True)
class CategoriesRequest(BasePaginationRequest):
    pass

CategoryRequestDescription = """The page of categories to get."""
