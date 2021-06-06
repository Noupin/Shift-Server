#pylint: disable=C0103, C0301
"""
The Individual User Get Response Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from marshmallow import fields, Schema

#First Party Imports
from src.DataModels.Marshmallow.User import UserSchema
from src.DataModels.Response.DefaultResponse import DefaultResponse


class IndividualUserGetResponse(Schema):
    user = fields.Nested(UserSchema)
    owner = fields.Boolean(required=True)

IndividualUserGetResponseDescription = f"""The requested user."""
