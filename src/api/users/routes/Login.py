#pylint: disable=C0103, C0301
"""
Login endpoint for the Users part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from flask import request
from flask_restful import Resource
from flask_apispec.annotations import doc
from flask_apispec.views import MethodResource
from flask_login import current_user, login_user
from flask_apispec import marshal_with, use_kwargs

#First Party Imports
from src import bcrypt
from src.DataModels.MongoDB.User import User
from src.DataModels.Response.LoginResponse import (LoginResponse,
                                                   LoginResponseDescription)
from src.DataModels.Request.LoginRequest import (LoginRequest,
                                                 LoginRequestDescription)


class Login(MethodResource, Resource):

    @use_kwargs(LoginRequest.Schema(),
                description=LoginRequestDescription)
    @marshal_with(LoginResponse.Schema(),
                  description=LoginResponseDescription)
    @doc(description="""The login for the user.""")
    def post(self, requestData: LoginRequest) -> dict:
        """
        The login for the user.
        """

        if current_user.is_authenticated:
            return {'msg': "You are already logged in"}
        
        if not request.is_json:
            return {'msg': "Your login had no JSON payload"}
        
        if not requestData.usernameOrEmail:
            return {'msg': "Username or Email missing"}
        
        if User.objects(email=requestData.usernameOrEmail).first():
            user = User.objects(email=requestData.usernameOrEmail).first()
        elif User.objects(username=requestData.usernameOrEmail).first():
            user = User.objects(username=requestData.usernameOrEmail).first()
        else:
            return {'msg': "Username or Email incorrect"}

        if bcrypt.check_password_hash(user.password, requestData.password):
            login_user(user, remember=requestData.remember)
        else:
            return {'msg': 'Login unsuccesful, password incorrect'}

        return {'msg': "Login success."}
