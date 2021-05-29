#pylint: disable=C0103, C0301
"""
The Update Picture Response Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from marshmallow_dataclass import dataclass

#First Party Imports
from src.DataModels.Response.DefaultResponse import DefaultResponse


@dataclass(frozen=True)
class UpdatePictureResponse(DefaultResponse):
    pass

UpdatePictureResponseDescription = """Whether the picture has been updated or not."""
