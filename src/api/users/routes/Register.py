#pylint: disable=C0103, C0301
"""
Register endpoint for the Users part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from flask import request
from flask_restful import Resource
from flask_apispec.annotations import doc
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, use_kwargs
from flask_login import login_user, current_user

#First Party Imports
from src import bcrypt
from src.DataModels.MongoDB.User import User
from src.utils.validators import validateEmail, validatePassword
from src.DataModels.Request.RegisterRequest import (RegisterRequest,
                                                    RegisterRequestDescription)
from src.DataModels.Response.RegisterResponse import (RegisterResponse,
                                                      RegisterResponseDescription)


class Register(MethodResource, Resource):

    @use_kwargs(RegisterRequest.Schema(),
                description=RegisterRequestDescription)
    @marshal_with(RegisterResponse.Schema(),
                  description=RegisterResponseDescription)
    @doc(description="""
         The regitration for the user.""")
    def post(self, requestData: RegisterRequest) -> dict:
        if current_user.is_authenticated:
            return {'msg': "You're already logged in"}
        
        if not request.is_json:
            return {'msg': "Your login had no JSON payload"}

        if User.objects(username=requestData.username).first():
            return {'msg': "A user with that username already exists"}
        if User.objects(email=requestData.email).first():
            return {'msg': "A user with that email already exists"}

        emailValid, emailMsg = validateEmail(requestData.email)
        if not emailValid:
            return {'msg': emailMsg}
        passwordValid, passwordMsg = validatePassword(requestData.password)
        if not passwordValid:
            return {'msg': passwordMsg}

        hashed_password = bcrypt.generate_password_hash(requestData.password)

        user = User(username=requestData.username, email=requestData.email, password=hashed_password)
        user.save()

        login_user(user, remember=True)
        
        return {"msg": "You have been registered succesfully"}
