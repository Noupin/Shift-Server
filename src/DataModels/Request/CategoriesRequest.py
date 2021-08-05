#pylint: disable=C0103, C0301
"""
The Categories Request Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from marshmallow_dataclass import dataclass


@dataclass(frozen=True)
class CategoriesRequest:
    page: int

CategoryRequestDescription = """The page of categories to get."""
