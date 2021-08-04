#pylint: disable=C0103, C0301
"""
Resend Confirmation Email endpoint for the Users part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from flask_restful import Resource
from flask_apispec import marshal_with, doc
from flask_apispec.views import MethodResource
from flask_jwt_extended import jwt_required, current_user

#First Party Imports
from src import mail
from src.utils.email import sendEmail
from src.variables.constants import AUTHORIZATION_TAG, CONFIRM_ACCOUNT_SUBJECT, confirmAccountMessageTemplate
from src.DataModels.Response.ResendConfirmEmailResponse import (ResendConfirmEmailResponse,
                                                                ResendConfirmEmailResponseDescription)


class ResendConfirmEmail(MethodResource, Resource):

    @marshal_with(ResendConfirmEmailResponse.Schema(),
                  description=ResendConfirmEmailResponseDescription)
    @doc(description="""Resends the email to confirm the user.""", tags=["Authenticate"],
operationId="resendConfirmEmail", security=AUTHORIZATION_TAG)
    @jwt_required(locations=['headers'])
    def get(self):
        sendEmail(mail, subject=CONFIRM_ACCOUNT_SUBJECT, recipients=[current_user.email],
                  msg=confirmAccountMessageTemplate(current_user.getConfirmationToken()))

        return ResendConfirmEmailResponse(msg=f"The email has been sent again to you, {current_user.username}.")
