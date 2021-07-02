#pylint: disable=C0103, C0301
"""
The Reset Password Request Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from marshmallow_dataclass import dataclass


@dataclass(frozen=True)
class ResetPasswordRequest:
    password: str

ResetPasswordRequestDescription = """The password to reset with."""
