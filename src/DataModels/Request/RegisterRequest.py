#pylint: disable=C0103, C0301
"""
The Login Request Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from marshmallow_dataclass import dataclass


@dataclass(frozen=True)
class RegisterRequest:
    username: str
    password: str
    email: str

RegisterRequestDescription = """
The name the user has picked for their account, \
the password associated with the username of the \
user logging in, and the email to be registered with \
the new account.
"""
