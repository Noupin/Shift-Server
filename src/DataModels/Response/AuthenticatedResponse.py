#pylint: disable=C0103, C0301
"""
The Authenticated Response Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from marshmallow import fields, Schema

#First Party Imports
from src.DataModels.Marshmallow.User import UserSchema


class AuthenticatedResponse(Schema):
    msg = fields.String(missing="")
    authenticated = fields.Boolean(missing=False)
    user = fields.Nested(UserSchema)

AuthenticatedResponseDescription = """Whether the use is authenticated or \
not and their user object if they are authenticated."""
