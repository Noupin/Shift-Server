#pylint: disable=C0103, C0301
"""
The Image Response Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
import werkzeug.datastructures
from marshmallow_dataclass import dataclass


@dataclass(frozen=True)
class VideoResponse:
    file: werkzeug.datastructures.FileStorage

VideoResponseDescription = """The video file requested as a download or file."""
