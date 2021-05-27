#pylint: disable=C0103, C0301
"""
Profile endpoint for the Users part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from flask_restful import Resource
from flask_apispec import marshal_with
from flask_apispec.annotations import doc
from flask_apispec.views import MethodResource
from flask_login import current_user, login_required

#First Party Imports
from src.DataModels.MongoDB.User import User
from src.variables.constants import SECURITY_TAG
from src.DataModels.Response.ProfileResponse import (ProfileResponse,
                                                     ProfileResponseDescription)


class Profile(MethodResource, Resource):
    decorators = [login_required]

    @marshal_with(ProfileResponse,
                  description=ProfileResponseDescription)
    @doc(description="""The users profile to display the on users the account page""", tags=["User"],
operationId="profile", security=SECURITY_TAG)
    def get(self) -> dict:
        userJSON = User.objects(id=current_user.id).first()

        return {"profile": userJSON}
