#pylint: disable=C0103, C0301
"""
Confirmation Email endpoint for the Users part of the Shift API
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
from src.decorators.confirmationRequired import confirmationRequired
from src.DataModels.Response.ConfirmEmailChangeResponse import (ConfirmEmailChangeResponse,
                                                                ConfirmEmailChangeResponseDescription)


class ConfirmEmailChange(MethodResource, Resource):

    @marshal_with(ConfirmEmailChangeResponse.Schema(),
                  description=ConfirmEmailChangeResponseDescription)
    @doc(description="""Confirms the change to the new users email.""", tags=["User"],
operationId="confirmEmailChange", security=AUTHORIZATION_TAG)
    @jwt_required(locations=['headers'])
    @confirmationRequired
    def get(self, token) -> dict:
        nextEmail, user = User.verifyChangeEmailToken(token)
        
        if user is None:
            if User.objects(email=nextEmail).first():
                return ConfirmEmailChangeResponse(msg="Your email has already been changed.", confirmed=True)
            return ConfirmEmailChangeResponse(msg="The token has expired or is invalid.")
        
        user.update(set__email=nextEmail)

        return ConfirmEmailChangeResponse(msg=f"You have confirmed your new email. Thank you {current_user.username}.", confirmed=True)
