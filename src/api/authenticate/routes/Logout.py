#pylint: disable=C0103, C0301
"""
Logout endpoint for the Users part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from flask import jsonify
from flask_restful import Resource
from datetime import datetime, timezone
from flask_apispec import marshal_with, doc
from flask_apispec.views import MethodResource
from flask_jwt_extended import (jwt_required, current_user,
                                get_jwt, unset_refresh_cookies)

#First Party Imports
from src.variables.constants import AUTHORIZATION_TAG
from src.DataModels.MongoDB.TokenBlocklist import TokenBlocklist
from src.DataModels.Response.LogoutResponse import (LogoutResponse,
                                                    LogoutResponseDescription)


class Logout(MethodResource, Resource):

    @marshal_with(LogoutResponse.Schema(),
                  description=LogoutResponseDescription)
    @doc(description="""Logs the user out.""", tags=["Authenticate"],
operationId="logout", security=AUTHORIZATION_TAG)
    @jwt_required(locations=['headers'])
    def get(self) -> dict:
        username = current_user.username
        jti = get_jwt()["jti"]
        now = datetime.now(timezone.utc)
        blockedToken = TokenBlocklist(jti=jti, createdAt=now)
        blockedToken.save()
        
        flaskResponse = jsonify(LogoutResponse(msg=f"Logout Successful as {username}"))
        unset_refresh_cookies(flaskResponse)

        return flaskResponse
