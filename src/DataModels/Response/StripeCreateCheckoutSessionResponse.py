#pylint: disable=C0103, C0301
"""
The Stripe Create Checkout Session Response Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from marshmallow_dataclass import dataclass


@dataclass(frozen=True)
class StripeCreateCheckoutSessionResponse:
    sessionId: str=""

StripeCreateCheckoutSessionResponseDescription = """The stripe session id."""
