#pylint: disable=C0103, C0301
"""
The Individual User Delete Response Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from marshmallow_dataclass import dataclass

#First Party Imports
from src.models.Response.DefaultResponse import DefaultResponse


@dataclass(frozen=True)
class IndividualUserDeleteResponse(DefaultResponse):
    pass

IndividualUserDeleteResponseDescription = f"""The status message pertaing to the delete."""
