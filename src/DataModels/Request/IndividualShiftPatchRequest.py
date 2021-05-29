#pylint: disable=C0103, C0301
"""
The Individual Shift Put Request Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from typing import Any
from marshmallow import fields
from marshmallow_dataclass import dataclass
from marshmallow_dataclass.union_field import Union


@dataclass(frozen=True)
class IndividualShiftPatchRequest:
    data: dict

IndividualShiftPatchRequestDescription = """The field name and updated value \
to update the queried shift."""
