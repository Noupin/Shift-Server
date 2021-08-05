#pylint: disable=C0103, C0301
"""
The Stripe Publishable Key Response Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from marshmallow_dataclass import dataclass


@dataclass(frozen=True)
class StripePublishableKeyResponse:
    publicKey: str

StripePublishableKeyResponseDescription = """The pubishable key."""
