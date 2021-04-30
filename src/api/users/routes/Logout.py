#pylint: disable=C0103, C0301
"""
Logout endpoint for the Users part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from flask_restful import Resource
from marshmallow import Schema, fields
from flask_apispec import marshal_with
from flask_apispec.views import MethodResource
from flask_login import logout_user, current_user, login_required


class LogoutRepsonse(Schema):
    msg = fields.String()

class Logout(MethodResource, Resource):
    decorators = [login_required]

    @marshal_with(LogoutRepsonse)
    def get(self) -> dict:
        """
        The logout for the user.
        """

        username = current_user.username
        logout_user()

        return {"msg": f"Logout Successful as {username}"}
