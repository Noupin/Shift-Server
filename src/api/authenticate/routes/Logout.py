#pylint: disable=C0103, C0301
"""
Logout endpoint for the Users part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from flask_restful import Resource
from flask_apispec import marshal_with, doc
from flask_apispec.views import MethodResource
from flask_login import logout_user, current_user, login_required

#First Party Imports
from src.variables.constants import SECURITY_TAG
from src.DataModels.Response.LogoutResponse import (LogoutResponse,
                                                    LogoutResponseDescription)


class Logout(MethodResource, Resource):
    decorators = [login_required]

    @marshal_with(LogoutResponse.Schema(),
                  description=LogoutResponseDescription)
    @doc(description="""Logs the user out.""", tags=["Authenticate"],
operationId="logout", security=SECURITY_TAG)
    def get(self) -> dict:
        username = current_user.username
        logout_user()

        return {"msg": f"Logout Successful as {username}"}