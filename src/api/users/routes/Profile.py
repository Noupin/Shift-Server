#pylint: disable=C0103, C0301
"""
Profile endpoint for the Users part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from flask_restful import Resource
from marshmallow import Schema, fields
from flask_apispec import marshal_with
from flask_apispec.views import MethodResource
from flask_login import current_user, login_required

#First Party Imports
from src.DataModels.MongoDB.User import User
from src.DataModels.Marshmallow.User import UserSchema


class ProfileResponse(Schema):
    profile = fields.Nested(UserSchema)

class Profile(MethodResource, Resource):
    decorators = [login_required]

    @marshal_with(ProfileResponse)
    def get(self) -> dict:
        """
        The users profile to display the on users the account page

        Returns:
            JSON: A JSON with the users profile to display on the users account page
        """

        userJSON = User.objects(id=current_user.id).first()

        return {"profile": userJSON}
