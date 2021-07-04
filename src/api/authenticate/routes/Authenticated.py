#pylint: disable=C0103, C0301
"""
Authentication endpoint for the Users part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from flask_restful import Resource
from flask_login import current_user
from flask_apispec import marshal_with, doc
from flask_apispec.views import MethodResource

#First Party Imports
from src.DataModels.MongoDB.User import User
from src.DataModels.Marshmallow.User import UserSchema
from src.DataModels.Response.AuthenticatedResponse import (AuthenticatedResponse,
                                                           AuthenticatedResponseDescription)


class Authenticated(MethodResource, Resource):

    @marshal_with(AuthenticatedResponse,
                  description=AuthenticatedResponseDescription)
    @doc(description="""Whether the user is logged in currently or not.""", tags=["Authenticate"],
operationId="authenticated")
    def get(self) -> dict:
        if current_user.is_authenticated:
            user = User.objects(id=current_user.id).first()
            userModel: UserSchema = UserSchema().dump(user)
            return AuthenticatedResponse().load(dict(msg="", authenticated=True, user=userModel))

        return AuthenticatedResponse().load(dict(msg="", authenticated=False))
