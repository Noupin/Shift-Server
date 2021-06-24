#pylint: disable=C0103, C0301
"""
The Register Response Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from marshmallow_dataclass import dataclass

#First Party Imports
from src.DataModels.Response.DefaultResponse import DefaultResponse


@dataclass(frozen=True)
class RegisterResponse(DefaultResponse):
    usernameMessage: str = ""
    emailMessage: str = ""
    passwordMessage: str = ""

RegisterResponseDescription = """The status of the register attempt, a specific \
message for the username, a specific message for the email, and a specific message \
for the password."""
