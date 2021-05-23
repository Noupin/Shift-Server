#pylint: disable=C0103, C0301
"""
The Media Request Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from marshmallow_dataclass import dataclass


@dataclass(frozen=True)
class MediaRequest:
    filename: str

MediaRequestDescription = """The name of the file to request."""
