#pylint: disable=C0103, C0301
"""
The Stop Train Response Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from marshmallow_dataclass import dataclass

#First Party Imports
from src.models.Response.DefaultResponse import DefaultResponse


@dataclass(frozen=True)
class StopTrainResponse(DefaultResponse):
    pass

StopTrainResponseDescription = """Whether the stop train signal was accepted."""
