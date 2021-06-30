#pylint: disable=C0103, C0301
"""
The Change Password Response Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from marshmallow_dataclass import dataclass

#First Party Imports
from src.DataModels.Response.DefaultResponse import DefaultResponse


@dataclass(frozen=True)
class ChangePasswordResponse(DefaultResponse):
    currentPasswordMessage: str = ""
    newPasswordMessage: str = ""

ChangePasswordResponseDescription = f"""The status message pertaing to the patch, \
the current password message, and the new password message."""
