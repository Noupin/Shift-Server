#pylint: disable=C0103, C0301
"""
The Image Response Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from marshmallow import Schema, fields


class ImageResponse(Schema):
    image = fields.Raw(type='image')

ImageResponseDescription = """The image file requested as a download or file."""
