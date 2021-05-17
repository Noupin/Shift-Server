#pylint: disable=C0103, C0301
"""
The Inference Response Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from marshmallow_dataclass import dataclass

#First Party Imports
from src.DataModels.Response.DefaultResponse import DefaultResponse


@dataclass(frozen=True)
class InferenceResponse(DefaultResponse):
    pass

InferenceResponseDescription = """Whether the shifting/inferencing went according to plan."""
