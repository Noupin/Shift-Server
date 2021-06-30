#pylint: disable=C0103, C0301
"""
Individual user endpoint for the user part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
import mongoengine
from typing import Union
from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask_login import login_required, current_user
from flask_apispec import marshal_with, doc, use_kwargs

#First Party Imports
from src import bcrypt
from src.DataModels.MongoDB.User import User
from src.variables.constants import SECURITY_TAG
from src.utils.validators import validatePassword
from src.DataModels.Request.ForgotPasswordRequest import (ForgotPasswordRequest,
                                                          ForgotPasswordRequestDescription)
from src.DataModels.Response.ForgotPasswordResponse import (ForgotPasswordResponse,
                                                            ForgotPasswordResponseDescription)


class ForgotPassword(MethodResource, Resource):
    
    @staticmethod
    def userExists(username: str) -> Union[User, dict]:
        try:
            return User.objects(username=username).first()
        except ValueError:
            return {}


    @use_kwargs(ForgotPasswordRequest.Schema(),
                description=ForgotPasswordRequestDescription)
    @marshal_with(ForgotPasswordResponse.Schema(),
                  description=ForgotPasswordResponseDescription)
    @doc(description="""Updates/modifies users password.""",
         tags=["User"], operationId="forgotPassword")
    def patch(self, uuid: str, requestBody: ForgotPasswordRequest):
        user = self.userExists(current_user.username)
        if not isinstance(user, User):
            return ForgotPasswordResponse(msg="""User was not modified because \
it does not exist.""")

        if(current_user.id != user.id):
            return ForgotPasswordResponse(msg="""You cannot modify a user that \
is not you.""")

        passwordValid, passwordMsg = validatePassword(requestBody.newPassword)
        if not passwordValid:
            return ForgotPasswordResponse(newPasswordMessage=passwordMsg)

        try:
            user.update(set__password=bcrypt.generate_password_hash(requestBody.newPassword).decode("utf-8"))
        except ValueError:
            return ForgotPasswordResponse(msg=f"The password field is \
not the same type as the value you submitted"), 500
        except TypeError:
            return ForgotPasswordResponse(msg=f"The password field is \
not the same type as the value you submitted"), 500
        except mongoengine.errors.OperationError:
            return ForgotPasswordResponse(msg=f"There was no data sent to update \
this would remove data."), 500

        return ForgotPasswordResponse(msg=f"The password for the User: {user.username} have been modified.")
