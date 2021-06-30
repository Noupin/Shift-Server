#pylint: disable=C0103, C0301
"""
The Forgot Password Response Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from marshmallow_dataclass import dataclass

#First Party Imports
from src.DataModels.Response.DefaultResponse import DefaultResponse


@dataclass(frozen=True)
class ForgotPasswordResponse(DefaultResponse):
    currentPasswordMessage: str = ""
    newPasswordMessage: str = ""

ForgotPasswordResponseDescription = f"""The status message pertaing to the patch, \
and the new password message."""
