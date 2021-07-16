#pylint: disable=C0103, C0301
"""
The Login Response Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from marshmallow_dataclass import dataclass

#First Party Imports
from src.DataModels.Response.DefaultResponse import DefaultResponse


@dataclass(frozen=True)
class LoginResponse(DefaultResponse):
    accessToken: str = ""
    usernameMessage: str = ""
    passwordMessage: str = ""

LoginResponseDescription = """The status of the login attempt, an access \
token to use for protected routes, a specific message for the username and \
a specific message for the password."""
