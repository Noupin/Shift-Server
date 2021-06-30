#pylint: disable=C0103, C0301
"""
The Change Password Request Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from marshmallow_dataclass import dataclass


@dataclass(frozen=True)
class ChangePasswordRequest:
    currentPassword: str
    newPassword: str

ChangePasswordRequestDescription = """The users current password \
to check and the new password to update to."""
