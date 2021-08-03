#pylint: disable=C0103, C0301
"""
Refresh endpoint for the Users part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs
from flask_jwt_extended import (jwt_required, get_jwt_identity,
                                create_access_token)

#First Party Imports
from src.DataModels.MongoDB.User import User
from src.variables.constants import COOKIE_REFRESH_TAG
from src.DataModels.Request.RefreshRequest import RefreshRequest
from src.DataModels.Response.RefreshResponse import (RefreshResponse,
                                                     RefreshResponseDescription)


class Refresh(MethodResource, Resource):

    @use_kwargs(RefreshRequest.Schema(), location="headers",
                description="The tokens required to refresh.")
    @marshal_with(RefreshResponse.Schema(),
                  description=RefreshResponseDescription)
    @doc(description="""Refreshes the users access token.""",
         tags=["Authenticate"], operationId="refresh", security=COOKIE_REFRESH_TAG)
    @jwt_required(refresh=True, locations=['headers', 'cookies'])
    def get(self, _: RefreshRequest):
        identity = get_jwt_identity()
        user = User.objects(id=identity).first()
        accessToken = create_access_token(identity=user)

        return RefreshResponse(msg="Refresh successful", accessToken=accessToken)
