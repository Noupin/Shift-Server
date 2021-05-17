#pylint: disable=C0103, C0301
"""
The Login Request Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from marshmallow_dataclass import dataclass


@dataclass(frozen=True)
class LoginRequest:
    usernameOrEmail: str
    password: str
    remember: bool = True

LoginRequestDescription = """The username or email of the user logging in, \
the password associated with the username of the user logging in, and whether \
or not the user should be remebered when they are logged in."""
