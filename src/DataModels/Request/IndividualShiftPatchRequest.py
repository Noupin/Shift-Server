#pylint: disable=C0103, C0301
"""
The Individual Shift Put Request Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from typing import Dict
from marshmallow_dataclass import dataclass


@dataclass(frozen=True)
class IndividualShiftPatchRequest:
    data: Dict[str, str]

IndividualShiftPatchRequestDescription = """The field name and updated value \
to update the queried shift."""
