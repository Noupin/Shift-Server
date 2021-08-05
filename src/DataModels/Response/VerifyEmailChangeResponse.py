#pylint: disable=C0103, C0301
"""
The Verify Email Change Response Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from typing import Optional
from marshmallow_dataclass import dataclass

#First Party Imports
from src.DataModels.Response.DefaultResponse import DefaultResponse


@dataclass(frozen=True)
class VerifyEmailChangeResponse(DefaultResponse):
    confirmed: bool = False
    nextEmail: str = ""

VerifyEmailChangeResponseDescription = """Whether the verifying of the email change
went according to plan and the next email to confirm."""
