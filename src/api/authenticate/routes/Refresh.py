#pylint: disable=C0103, C0301
"""
Refresh endpoint for the Users part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from flask_restful import Resource
from flask_apispec import marshal_with, doc
from flask_apispec.views import MethodResource
from flask_jwt_extended import (jwt_required, get_jwt_identity,
                                create_access_token)

#First Party Imports
from src.DataModels.MongoDB.User import User
from src.variables.constants import REFRESH_TAG
from src.DataModels.Response.RefreshResponse import (RefreshResponse,
                                                     RefreshResponseDescription)


class Refresh(MethodResource, Resource):

    @marshal_with(RefreshResponse.Schema(),
                  description=RefreshResponseDescription)
    @doc(description="""Refreshes the users access token.""",
         tags=["Authenticate"], operationId="refresh", security=REFRESH_TAG)
    @jwt_required(refresh=True, locations=["cookies", "headers"])
    def get(self):
        identity = get_jwt_identity()
        user = User.objects(id=identity).first()
        accessToken = create_access_token(identity=user)

        return RefreshResponse(msg="Refresh successful", accessToken=accessToken)
