#pylint: disable=C0103, C0301
"""
Individual user endpoint for the user part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
import os
import mongoengine
from typing import Union
from flask import current_app
from flask_restful import Resource
from datetime import datetime, timezone
from flask_apispec.views import MethodResource
from src.DataModels.Marshmallow.User import UserSchema
from flask_apispec import marshal_with, doc, use_kwargs
from flask_jwt_extended import jwt_required, current_user, get_jwt

#First Party Imports
from src.DataModels.MongoDB.User import User
from src.utils.validators import validateEmail, validateUsername
from src.DataModels.MongoDB.TokenBlocklist import TokenBlocklist
from src.variables.constants import IMAGE_PATH, AUTHORIZATION_TAG, USER_EDITABLE_USER_FIELDS
from src.DataModels.Request.IndividualUserPatchRequest import (IndividualUserPatchRequest,
                                                               IndividualUserPatchRequestDescription)
from src.DataModels.Response.IndividualUserGetResponse import (IndividualUserGetResponse,
                                                               IndividualUserGetResponseDescription)
from src.DataModels.Response.IndividualUserPatchResponse import (IndividualUserPatchResponse,
                                                                 IndividualUserPatchResponseDescription)
from src.DataModels.Response.IndividualUserDeleteResponse import (IndividualUserDeleteResponse,
                                                                  IndividualUserDeleteResponseDescription)


class IndividualUser(MethodResource, Resource):
    
    @staticmethod
    def userExists(username: str) -> Union[User, dict]:
        try:
            return User.objects(username=username).first()
        except ValueError:
            return {}


    @marshal_with(IndividualUserGetResponse,
                  description=IndividualUserGetResponseDescription)
    @doc(description="""The queried user.""", tags=["User"],
         operationId="getIndivdualUser", security=AUTHORIZATION_TAG)
    @jwt_required(optional=True)
    def get(self, username: str):
        user = self.userExists(username)
        if not isinstance(user, User):
            return IndividualUserGetResponse(), 404

        userModel: UserSchema = UserSchema().dump(user)
        
        userID = ""
        if current_user:
            userID = current_user.id

        return IndividualUserGetResponse().load(dict(user=userModel,
                                                     owner=userID==user.id))


    @marshal_with(IndividualUserDeleteResponse.Schema(),
                  description=IndividualUserDeleteResponseDescription)
    @doc(description="""Deletes the queried user.""",
         tags=["User"], operationId="deleteIndivdualUser", security=AUTHORIZATION_TAG)
    @jwt_required()
    def delete(self, username: str):
        user = self.userExists(username)
        if not isinstance(user, User):
            return IndividualUserDeleteResponse(msg="User was not deleted because \
it does not exist.")
        
        if(current_user.id != user.id):
            return IndividualUserDeleteResponse(msg="You cannot delete a user that \
is not you.")
        
        username = user.username
        
        if user.mediaFilename.find("default") == -1:
            os.remove(os.path.join(current_app.root_path, IMAGE_PATH, user.mediaFilename))
        jti = get_jwt()["jti"]
        now = datetime.now(timezone.utc)
        blockedToken = TokenBlocklist(jti=jti, createdAt=now)
        blockedToken.save()
        user.delete()
        
        return IndividualUserDeleteResponse(msg=f"User: {username} has been deleted")


    @use_kwargs(IndividualUserPatchRequest.Schema(),
                description=IndividualUserPatchRequestDescription)
    @marshal_with(IndividualUserPatchResponse.Schema(),
                  description=IndividualUserPatchResponseDescription)
    @doc(description="""Updates/modifies the queried user.""",
         tags=["User"], operationId="patchIndivdualUser", security=AUTHORIZATION_TAG)
    @jwt_required()
    def patch(self, requestBody: IndividualUserPatchRequest, username: str):
        user = self.userExists(username)
        if not isinstance(user, User):
            return IndividualUserPatchResponse(msg="""User was not modified because \
it does not exist.""")

        if(current_user.id != user.id):
            return IndividualUserPatchResponse(msg="""You cannot modify a user that \
is not you.""")

        queries = {}
        for field, value in requestBody.data.items():
            if field not in USER_EDITABLE_USER_FIELDS:
                return IndividualUserPatchResponse(msg="You are not allowed to change this field.")
            
            elif field == "username":
                if User.objects(username=value).first():
                    return IndividualUserPatchResponse(msg="A user with that username already exists")
                
                if not validateUsername(value):
                    return IndividualUserPatchResponse(msg="That is not a valid username.")
                
                queries[f"set__{field}"] = value

            elif field == "email":
                emailValid, emailMsg = validateEmail(value)
                if not emailValid:
                    return IndividualUserPatchResponse(msg=emailMsg)
                if User.objects(email=value).first():
                    return IndividualUserPatchResponse(msg="A user with that email already exists")
                queries[f"set__{field}"] = value

        try:
            user.update(**queries)
        except ValueError:
            return IndividualUserPatchResponse(msg=f"The field you are changing is \
not the same type as the value you submitted"), 500
        except TypeError:
            return IndividualUserPatchResponse(msg=f"The field you are changing is \
not the same type as the value you submitted"), 500
        except mongoengine.errors.OperationError:
            return IndividualUserPatchResponse(msg=f"There was no data sent to update \
this would remove data."), 500

        return IndividualUserPatchResponse(msg=f"The fields \
{[field for field, _ in requestBody.data.items()]} for the User: {user.username} have been modified.")
