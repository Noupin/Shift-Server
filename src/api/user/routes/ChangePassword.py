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
from flask_apispec import marshal_with, doc, use_kwargs
from flask_jwt_extended import jwt_required, current_user

#First Party Imports
from src import bcrypt
from src.DataModels.MongoDB.User import User
from src.variables.constants import AUTHORIZATION_TAG
from src.utils.validators import validatePassword
from src.DataModels.Request.ChangePasswordRequest import (ChangePasswordRequest,
                                                          ChangePasswordRequestDescription)
from src.DataModels.Response.ChangePasswordResponse import (ChangePasswordResponse,
                                                            ChangePasswordResponseDescription)


class ChangePassword(MethodResource, Resource):
    
    @staticmethod
    def userExists(username: str) -> Union[User, dict]:
        try:
            return User.objects(username=username).first()
        except ValueError:
            return {}


    @use_kwargs(ChangePasswordRequest.Schema(),
                description=ChangePasswordRequestDescription)
    @marshal_with(ChangePasswordResponse.Schema(),
                  description=ChangePasswordResponseDescription)
    @doc(description="""Updates/modifies users password.""",
         tags=["User"], operationId="changePassword", security=AUTHORIZATION_TAG)
    @jwt_required()
    def patch(self, requestData: ChangePasswordRequest):
        user = self.userExists(current_user.username)
        if not isinstance(user, User):
            return ChangePasswordResponse(msg="""User was not modified because \
it does not exist.""")

        if(current_user.id != user.id):
            return ChangePasswordResponse(msg="""You cannot modify a user that \
is not you.""")

        seasonedRequestPassword = f"{requestData.currentPassword}{user.passwordSalt}"
        if not bcrypt.check_password_hash(current_user.password, seasonedRequestPassword):
            return ChangePasswordResponse(currentPasswordMessage="The password you entered does not match your current password.")

        passwordValid, passwordMsg = validatePassword(requestData.newPassword)
        if not passwordValid:
            return ChangePasswordResponse(newPasswordMessage=passwordMsg)

        try:
            passwordSalt = pyBcrypt.gensalt().decode("utf-8")
            seasonedPassword = f"{requestData.newPassword}{passwordSalt}"
            user.update(set__password=bcrypt.generate_password_hash(seasonedPassword).decode("utf-8"), set__passwordSalt=passwordSalt)
        except ValueError:
            return ChangePasswordResponse(msg=f"The password field is \
not the same type as the value you submitted"), 500
        except TypeError:
            return ChangePasswordResponse(msg=f"The password field is \
not the same type as the value you submitted"), 500
        except mongoengine.errors.OperationError:
            return ChangePasswordResponse(msg=f"There was no data sent to update \
this would remove data."), 500

        return ChangePasswordResponse(msg=f"The password for the User: {user.username} have been modified.", complete=True)
