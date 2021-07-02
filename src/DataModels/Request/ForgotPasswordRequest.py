#pylint: disable=C0103, C0301
"""
The Forgot Password Request Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from marshmallow_dataclass import dataclass


@dataclass(frozen=True)
class ForgotPasswordRequest:
    email: str

ForgotPasswordRequestDescription = """The email of the user to send the reset \
password token to."""
