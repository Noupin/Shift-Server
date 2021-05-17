#pylint: disable=C0103, C0301
"""
The Inference Status Response Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from marshmallow_dataclass import dataclass

#First Party Imports
from src.DataModels.Response.DefaultResponse import DefaultResponse


@dataclass(frozen=True)
class InferenceStatusReponse(DefaultResponse):
    stopped: bool
    imagePath: str

InferenceStatusReponseDescription = """A msg describing the current state of \
inferencing on the original media, whether or not the inferencing has been \
stopped or finished, and the image path to pass to the cdn."""
