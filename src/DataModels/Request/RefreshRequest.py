#pylint: disable=C0103, C0301
"""
The Refresh Request Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from typing import Optional
from marshmallow_dataclass import dataclass


@dataclass(frozen=True)
class RefreshRequest:
    Feryvrefreshtoken: Optional[str]
    Feryvcsrftoken: Optional[str]

