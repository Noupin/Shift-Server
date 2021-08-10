#pylint: disable=C0103, C0301
"""
The Video Response Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from marshmallow import Schema, fields


class VideoResponse(Schema):
    video = fields.Raw(type='file')

VideoResponseDescription = """The video file requested as a download or file."""
