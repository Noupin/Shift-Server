#pylint: disable=C0103, C0301
"""
The Reset Password Response Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from marshmallow_dataclass import dataclass

#First Party Imports
from src.DataModels.Response.DefaultResponse import DefaultResponse


@dataclass(frozen=True)
class ResetPasswordResponse(DefaultResponse):
    newPasswordMessage: str = ""
    complete: bool = False

ResetPasswordResponseDescription = f"""The status message pertaing to the patch, \
the current password message and whether the reset was completed."""
