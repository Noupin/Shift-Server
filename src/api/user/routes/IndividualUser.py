#pylint: disable=C0103, C0301
"""
Individual shift endpoint for the shift part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
import os
from typing import Union
from flask import current_app
from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask_login import login_required, current_user
from src.DataModels.Marshmallow.User import UserSchema
from flask_apispec import marshal_with, doc, use_kwargs

#First Party Imports
from src.DataModels.MongoDB.User import User
from src.variables.constants import IMAGE_PATH
from src.DataModels.Response.IndividualUserGetResponse import (IndividualUserGetResponse,
                                                               IndividualShiftGetResponseDescription)


class IndividualUser(MethodResource, Resource):
    
    @staticmethod
    def userExists(username: str) -> Union[User, dict]:
        try:
            return User.objects(username=username).first()
        except ValueError:
            return {}

    @marshal_with(IndividualUserGetResponse,
                  description=IndividualShiftGetResponseDescription)
    @doc(description="""The queried user""",
         tags=["User"], operationId="getIndivdualUser")
    def get(self, username: str):
        user = self.userExists(username)
        if not isinstance(user, User):
            return IndividualUserGetResponse()

        userModel: UserSchema = UserSchema().dump(user)

        return IndividualUserGetResponse().load(dict(shift=userModel))