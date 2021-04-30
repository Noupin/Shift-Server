#pylint: disable=C0103, C0301
"""
Authentication endpoint for the Users part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from flask_restful import Resource
from flask_login import current_user
from marshmallow import Schema, fields
from flask_apispec import marshal_with
from flask_apispec.views import MethodResource


class AuthenticatedResponse(Schema):
    authenticated = fields.Boolean()

class Authenticated(MethodResource, Resource):

    @marshal_with(AuthenticatedResponse)
    def get(self) -> dict:
        """
        Whether the user is logged in currently or not
        """

        if current_user.is_authenticated:
            return {'authenticated': True}

        return {'authenticated': False}
