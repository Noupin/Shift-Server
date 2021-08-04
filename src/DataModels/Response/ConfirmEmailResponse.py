#pylint: disable=C0103, C0301
"""
The Confirm Email Response Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from marshmallow_dataclass import dataclass

#First Party Imports
from src.DataModels.Response.DefaultResponse import DefaultResponse


@dataclass(frozen=True)
class ConfirmEmailResponse(DefaultResponse):
    confirmed: bool = False

ConfirmEmailResponseDescription = """The status of the user confirming their email."""
