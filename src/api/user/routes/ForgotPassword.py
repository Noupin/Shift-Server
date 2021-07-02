#pylint: disable=C0103, C0301
"""
Individual user endpoint for the user part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from typing import Union
from flask_restful import Resource
from flask_login import current_user
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs

#First Party Imports
from src import mail
from src.DataModels.MongoDB.User import User
from src.utils.validators import validateEmail
from src.utils.email import sendForgotPasswordEmail
from src.DataModels.Request.ForgotPasswordRequest import (ForgotPasswordRequest,
                                                          ForgotPasswordRequestDescription)
from src.DataModels.Response.ForgotPasswordResponse import (ForgotPasswordResponse,
                                                            ForgotPasswordResponseDescription)


class ForgotPassword(MethodResource, Resource):

    @use_kwargs(ForgotPasswordRequest.Schema(),
                description=ForgotPasswordRequestDescription)
    @marshal_with(ForgotPasswordResponse.Schema(),
                  description=ForgotPasswordResponseDescription)
    @doc(description="""Updates/modifies users password.""",
         tags=["User"], operationId="forgotPassword")
    def post(self, requestBody: ForgotPasswordRequest):
        if current_user.is_authenticated:
            return ForgotPasswordResponse(msg="You are already logged in.")

        emailValid, emailMsg = validateEmail(requestBody.email)
        if not emailValid:
            return ForgotPasswordResponse(emailMessage=emailMsg)

        user: User = User.objects(email=requestBody.email).first()
        if user is None:
            return ForgotPasswordResponse(msg="There is no account with that email please register.")

        sendForgotPasswordEmail(mail, user)

        return ForgotPasswordResponse(msg="Email Sent!", complete=True)
