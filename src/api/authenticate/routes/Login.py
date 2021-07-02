#pylint: disable=C0103, C0301
"""
Login endpoint for the Users part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from flask import request
from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask_login import current_user, login_user
from flask_apispec import marshal_with, use_kwargs, doc

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
    @doc(description="""The login for the user.""", tags=["Authenticate"], operationId="login")
    def post(self, requestData: LoginRequest) -> dict:
        """
        The login for the user.
        """

        if current_user.is_authenticated:
            return LoginResponse(msg="You are already logged in.")
        
        if not request.is_json:
            return LoginResponse(msg="Your login had no JSON payload.")
        
        if not requestData.usernameOrEmail:
            return LoginResponse(msg="Login Unsuccesful.",
                                 usernameMessage="Username or Email missing.")
        
        if User.objects(email=requestData.usernameOrEmail).first():
            user: User = User.objects(email=requestData.usernameOrEmail).first()
        elif User.objects(username=requestData.usernameOrEmail).first():
            user: User = User.objects(username=requestData.usernameOrEmail).first()
        else:
            return LoginResponse(msg="Login Unsuccesful.",
                                 usernameMessage="Username or Email incorrect.")

        seasonedRequestPassword = f"{requestData.password}{user.passwordSalt}"
        if bcrypt.check_password_hash(user.password, seasonedRequestPassword):
            login_user(user, remember=requestData.remember)
        else:
            return LoginResponse(msg="Login Unsuccesful.",
                                passwordMessage="Password incorrect.")

        return LoginResponse(msg="Login success.")