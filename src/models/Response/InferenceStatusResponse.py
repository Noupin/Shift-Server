#pylint: disable=C0103, C0301
"""
The Inference Status Response Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from typing import Optional
from marshmallow_dataclass import dataclass

#First Party Imports
from src.models.Response.DefaultResponse import DefaultResponse


@dataclass(frozen=True)
class InferenceStatusResponse(DefaultResponse):
    stopped: Optional[bool] = False
    mediaFilename: Optional[str] = None
    baseMediaFilename: Optional[str] = None
    maskMediaFilename: Optional[str] = None

InferenceStatusResponseDescription = """A msg describing the current state of \
inferencing on the original media, whether or not the inferencing has been \
stopped or finished, and the image path to pass to the cdn for the shifted media, \
and the base and the mask previews."""
