#pylint: disable=C0103, C0301
"""
The Profile Response Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from marshmallow import Schema, fields

#First Party Imports
from src.DataModels.Marshmallow.User import UserSchema


class ProfileResponse(Schema):
    profile = fields.Nested(UserSchema)

ProfileResponseDescription = """The profile for the user who is logged in."""
