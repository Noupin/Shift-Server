#pylint: disable=C0103, C0301
"""
Confirmation Email endpoint for the Users part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from src.utils.email import sendEmail
from flask_restful import Resource
from flask_apispec import marshal_with, doc
from flask_apispec.views import MethodResource
from flask_jwt_extended import jwt_required, current_user

#First Party Imports
from src import mail
from src.DataModels.MongoDB.User import User
from src.decorators.confirmationRequired import confirmationRequired
from src.variables.constants import (AUTHORIZATION_TAG, VERIFY_EMAIL_CHANGE_SUBJECT,
                                     confirmEmailChangeMessageTemplate)
from src.DataModels.Response.VerifyEmailChangeResponse import (VerifyEmailChangeResponse,
                                                               VerifyEmailChangeResponseDescription)


class VerifyEmailChange(MethodResource, Resource):

    @marshal_with(VerifyEmailChangeResponse.Schema(),
                  description=VerifyEmailChangeResponseDescription)
    @doc(description="""Verifies the server to send a confirmation email to the next email
address.""", tags=["User"], operationId="verifyEmailChange", security=AUTHORIZATION_TAG)
    @jwt_required(locations=['headers'])
    @confirmationRequired
    def get(self, token) -> dict:
        nextEmail, user = User.verifyChangeEmailToken(token)
        
        if user is None:
            return VerifyEmailChangeResponse(msg="The token has expired or is invalid.")
        
        sendEmail(mail, subject=VERIFY_EMAIL_CHANGE_SUBJECT, recipients=[nextEmail],
                  msg=confirmEmailChangeMessageTemplate(user.getChangeEmailToken(nextEmail)))

        return VerifyEmailChangeResponse(msg=f"You have verified your email to be changed. Please confirm your new email.",
                                         confirmed=True, nextEmail=nextEmail)
