#pylint: disable=C0103, C0301
"""
Confirm endpoint for the Users part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from flask_restful import Resource
from flask_apispec import marshal_with, doc
from flask_apispec.views import MethodResource
from flask_jwt_extended import jwt_required, current_user

#First Party Imports
from src.DataModels.MongoDB.User import User
from src.variables.constants import AUTHORIZATION_TAG
from src.DataModels.Response.ConfirmEmailResponse import (ConfirmEmailResponse,
                                                          ConfirmEmailResponseDescription)


class ConfirmEmail(MethodResource, Resource):

    @marshal_with(ConfirmEmailResponse.Schema(),
                  description=ConfirmEmailResponseDescription)
    @doc(description="""Confirms the users email.""", tags=["Authenticate"],
operationId="confirmEmail", security=AUTHORIZATION_TAG)
    @jwt_required(locations=['headers'])
    def get(self, token) -> dict:
        user = User.verifyConfimationToken(token)
        
        if user is None:
            return ConfirmEmailResponse(msg="The token has expired.")
        
        if user.confirmed:
            return ConfirmEmailResponse(msg="Your account has already been confirmed please login.", confirmed=True)
        else:
            user.update(set__confirmed=True)

        return ConfirmEmailResponse(msg=f"You have confirmed your account. Thank you {current_user.username}.", confirmed=True)
