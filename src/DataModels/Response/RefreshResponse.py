#pylint: disable=C0103, C0301
"""
The Refresh Response Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from marshmallow_dataclass import dataclass

#First Party Imports
from src.DataModels.Response.DefaultResponse import DefaultResponse


@dataclass(frozen=True)
class RefreshResponse(DefaultResponse):
    accessToken: str = ""

RefreshResponseDescription = """The status of the refresh attempt, an access \
token to use for protected routes."""
