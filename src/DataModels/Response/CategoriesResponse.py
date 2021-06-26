#pylint: disable=C0103, C0301
"""
The Categories Response Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from typing import List
from dataclasses import field
from marshmallow_dataclass import dataclass

#First Party Imports
from src.DataModels.Response.DefaultResponse import DefaultResponse


@dataclass(frozen=True)
class CategoriesResponse(DefaultResponse):
    categories: List[str]=field(default_factory=lambda: [])

categoriesResponseDescription = """The category names for the requested \
amount of categories."""
