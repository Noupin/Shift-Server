#pylint: disable=C0103, C0301
"""
The Authenticated Response Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from marshmallow_dataclass import dataclass

#First Party Imports
from src.DataModels.Response.DefaultResponse import DefaultResponse


@dataclass(frozen=True)
class AuthenticatedResponse(DefaultResponse):
    authenticated: bool

AuthenticatedResponseDescription = """Whether the use is authenticated or not."""
