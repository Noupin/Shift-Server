#pylint: disable=C0103, C0301
"""
The Image Response Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
import werkzeug.datastructures
from marshmallow_dataclass import dataclass


@dataclass(frozen=True)
class ImageResponse:
    file: werkzeug.datastructures.FileStorage

ImageResponseDescription = """The image file requested as a download or file."""
