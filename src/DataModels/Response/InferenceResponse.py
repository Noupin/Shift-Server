#pylint: disable=C0103, C0301
"""
The Inference Response Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from marshmallow_dataclass import dataclass


@dataclass(frozen=True)
class InferenceResponse:
    msg: str

InferenceResponseDescription = """
Whether the shifting/inferencing went according to plan. \
"""
