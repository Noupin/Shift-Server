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
         tags=["User"], operationId="changePassword", security=SECURITY_TAG)
    @login_required
    def patch(self, requestBody: ChangePasswordRequest):
        user = self.userExists(current_user.username)
        if not isinstance(user, User):
            return ChangePasswordResponse(msg="""User was not modified because \
it does not exist.""")

        if(current_user.id != user.id):
            return ChangePasswordResponse(msg="""You cannot modify a user that \
is not you.""")
            
        if not bcrypt.check_password_hash(current_user.password, requestBody.currentPassword):
            return ChangePasswordResponse(currentPasswordMessage="The password you entered does not match your current password.")

        passwordValid, passwordMsg = validatePassword(requestBody.newPassword)
        if not passwordValid:
            return ChangePasswordResponse(newPasswordMessage=passwordMsg)

        try:
            user.update(set__password=bcrypt.generate_password_hash(requestBody.newPassword).decode("utf-8"))
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
