#pylint: disable=C0103, C0301
"""
The Individual Shift Put Request Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from marshmallow_dataclass import dataclass


@dataclass(frozen=True)
class IndividualUserPatchRequest:
    data: dict

IndividualUserPatchRequestDescription = """The field name and updated value \
to update the queried user."""
