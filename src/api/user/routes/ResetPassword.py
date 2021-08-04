#pylint: disable=C0103, C0301
"""
Individual user endpoint for the user part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
import mongoengine
from typing import Union
import bcrypt as pyBcrypt
from flask_restful import Resource
from flask_apispec.views import MethodResource
from src.variables.constants import AUTHORIZATION_TAG
from flask_apispec import marshal_with, doc, use_kwargs
from flask_jwt_extended import current_user, jwt_required

#First Party Imports
from src import bcrypt
from src.DataModels.MongoDB.User import User
from src.utils.validators import validatePassword
from src.DataModels.Request.ResetPasswordRequest import (ResetPasswordRequest,
                                                         ResetPasswordRequestDescription)
from src.DataModels.Response.ResetPasswordResponse import (ResetPasswordResponse,
                                                           ResetPasswordResponseDescription)


class ResetPassword(MethodResource, Resource):
    
    @staticmethod
    def userExists(username: str) -> Union[User, dict]:
        try:
            return User.objects(username=username).first()
        except ValueError:
            return {}


    @use_kwargs(ResetPasswordRequest.Schema(),
                description=ResetPasswordRequestDescription)
    @marshal_with(ResetPasswordResponse.Schema(),
                  description=ResetPasswordResponseDescription)
    @doc(description="""Updates/modifies users password.""", tags=["User"],
         operationId="resetPassword", security=AUTHORIZATION_TAG)
    @jwt_required(optional=True)
    def patch(self, requestData: ResetPasswordRequest, token: str):
        if current_user:
            return ResetPasswordResponse(msg="You are already logged in.")

        user = User.verifyResetToken(token)
        
        if user is None:
            return ResetPasswordResponse(msg="The token has expired.")
        
        if not user.confirmed:
            return ResetPasswordResponse(msg="Please confirm your email before you reset your password")

        passwordValid, passwordMsg = validatePassword(requestData.password)
        if not passwordValid:
            return ResetPasswordResponse(newPasswordMessage=passwordMsg)

        try:
            passwordSalt = pyBcrypt.gensalt().decode("utf-8")
            seasonedPassword = f"{requestData.password}{passwordSalt}"
            user.update(set__password=bcrypt.generate_password_hash(seasonedPassword).decode("utf-8"), set__passwordSalt=passwordSalt)
        except ValueError:
            return ResetPasswordResponse(msg=f"The password field is \
not the same type as the value you submitted"), 500
        except TypeError:
            return ResetPasswordResponse(msg=f"The password field is \
not the same type as the value you submitted"), 500
        except mongoengine.errors.OperationError:
            return ResetPasswordResponse(msg=f"There was no data sent to update \
this would remove data."), 500

        return ResetPasswordResponse(msg=f"The password for the User: {user.username} have been modified.", complete=True)
