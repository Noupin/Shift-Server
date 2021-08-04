#pylint: disable=C0103, C0301
"""
Individual user endpoint for the user part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from flask_restful import Resource
from flask_apispec.views import MethodResource
from src.variables.constants import AUTHORIZATION_TAG, FORGOT_PASSWORD_SUBJECT, forgotPasswordMessageTemplate
from flask_apispec import marshal_with, doc, use_kwargs
from flask_jwt_extended import current_user, jwt_required

#First Party Imports
from src import mail
from src.utils.email import sendEmail
from src.DataModels.MongoDB.User import User
from src.utils.validators import validateEmail
from src.DataModels.Request.ForgotPasswordRequest import (ForgotPasswordRequest,
                                                          ForgotPasswordRequestDescription)
from src.DataModels.Response.ForgotPasswordResponse import (ForgotPasswordResponse,
                                                            ForgotPasswordResponseDescription)


class ForgotPassword(MethodResource, Resource):

    @use_kwargs(ForgotPasswordRequest.Schema(),
                description=ForgotPasswordRequestDescription)
    @marshal_with(ForgotPasswordResponse.Schema(),
                  description=ForgotPasswordResponseDescription)
    @doc(description="""Updates/modifies users password.""", tags=["User"],
         operationId="forgotPassword", security=AUTHORIZATION_TAG)
    @jwt_required(optional=True)
    def post(self, requestBody: ForgotPasswordRequest):
        if current_user:
            return ForgotPasswordResponse(msg="You are already logged in.")

        emailValid, emailMsg = validateEmail(requestBody.email)
        if not emailValid:
            return ForgotPasswordResponse(emailMessage=emailMsg)

        user: User = User.objects(email=requestBody.email).first()
        if user is None:
            return ForgotPasswordResponse(msg="There is no account with that email please register.")

        if not user.confirmed:
            return ForgotPasswordResponse(msg="Please confirm your email before you reset your password")

        sendEmail(mail, subject=FORGOT_PASSWORD_SUBJECT, recipients=[user.email],
                  msg=forgotPasswordMessageTemplate(user.getResetToken()))

        return ForgotPasswordResponse(msg="Email Sent!", complete=True)
