#pylint: disable=C0103, C0301
"""
The Login Response Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from marshmallow_dataclass import dataclass

#First Party Imports
from src.DataModels.Response.DefaultResponse import DefaultResponse


@dataclass(frozen=True)
class LoadDataResponse(DefaultResponse):
    shiftUUID: str = ""
    

LoadResponseDescription = """Given training data Shift specializes a \
model for the training data. Yeilds more relaisitic results than just \
an inference though it takes longer."""
