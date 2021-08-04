#pylint: disable=C0103, C0301
"""
The Confirm Email Request Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from marshmallow_dataclass import dataclass


@dataclass(frozen=True)
class ConfirmEmailRequest:
    token: str

ConfirmEmailRequestDescription = """The token to confirm the email with."""
