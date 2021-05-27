#pylint: disable=C0103, C0301
"""
The Train Response Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from typing import List, Optional
from marshmallow_dataclass import dataclass

#First Party Imports
from src.DataModels.Response.DefaultResponse import DefaultResponse


@dataclass(frozen=True)
class TrainStatusResponse(DefaultResponse):
    stopped: Optional[bool]
    exhibit: Optional[List[str]]

TrainStatusResponseDescription = """The status of the current shift training, \
whether the training has stopped, and encoded images to view on the front end."""
