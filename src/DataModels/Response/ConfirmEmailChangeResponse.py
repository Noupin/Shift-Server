#pylint: disable=C0103, C0301
"""
The Confirm Email Change Response Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from marshmallow_dataclass import dataclass

#First Party Imports
from src.DataModels.Response.DefaultResponse import DefaultResponse


@dataclass(frozen=True)
class ConfirmEmailChangeResponse(DefaultResponse):
    confirmed: bool = False

ConfirmEmailChangeResponseDescription = """Whether the confirming of the email change went according to plan."""
