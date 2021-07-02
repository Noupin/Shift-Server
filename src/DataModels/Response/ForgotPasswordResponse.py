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
    emailMessage: str = ""
    complete: bool = False

ForgotPasswordResponseDescription = f"""The status message pertaing to the patch, \
the new email message, and whether the request was completed."""
