#pylint: disable=C0103, C0301
"""
The Login Response Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from typing import Optional
from marshmallow_dataclass import dataclass


@dataclass(frozen=True)
class DefaultResponse:
    msg: Optional[str]
