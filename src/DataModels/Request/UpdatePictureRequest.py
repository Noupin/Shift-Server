#pylint: disable=C0103, C0301
"""
The Update Picture Request Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from marshmallow.schema import Schema

#First Party Imports
from src.DataModels.Marshmallow.FileField import FileField


class UpdatePictureRequest(Schema):
    requestFiles = FileField(required=True)

UpdatePictureRequestDescription = """The image to update the profile picture to."""
