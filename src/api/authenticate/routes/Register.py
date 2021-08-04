#pylint: disable=C0103, C0301
"""
Register endpoint for the Users part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
import bcrypt as pyBcrypt
from flask import request, jsonify
from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, use_kwargs, doc
from flask_jwt_extended import (create_access_token, current_user,
                                jwt_required, create_refresh_token,
                                set_refresh_cookies)

#First Party Imports
from src import bcrypt, mail
from src.utils.email import sendEmail
from src.DataModels.MongoDB.User import User
from src.DataModels.Request.RegisterRequest import (RegisterRequest,
                                                    RegisterRequestDescription)
from src.DataModels.Response.RegisterResponse import (RegisterResponse,
                                                      RegisterResponseDescription)
from src.variables.constants import (AUTHORIZATION_TAG, CONFIRM_ACCOUNT_SUBJECT,
                                     confirmAccountMessageTemplate)
from src.utils.validators import validateEmail, validatePassword, validateUsername


class Register(MethodResource, Resource):

    @use_kwargs(RegisterRequest.Schema(),
                description=RegisterRequestDescription)
    @marshal_with(RegisterResponse.Schema(),
                  description=RegisterResponseDescription)
    @doc(description="""The regitration for the user.""", tags=["Authenticate"],
         operationId="register", security=AUTHORIZATION_TAG)
    @jwt_required(optional=True)
    def post(self, requestData: RegisterRequest) -> dict:
        if current_user:
            return RegisterResponse(msg="You're already logged in.")
        
        if not request.is_json:
            return RegisterResponse(msg="Your register had no JSON payload")

        if User.objects(username=requestData.username).first():
            return RegisterResponse(msg="Registration Unsuccesful.",
                                    usernameMessage="A user with that username already exists.")
        if not validateUsername(requestData.username):
            return RegisterResponse(msg="Registration Unsuccesful.",
                                    usernameMessage="That is not a valid username.")
        if User.objects(email=requestData.email).first():
            return RegisterResponse(msg="Registration Unsuccesful.",
                                    emailMessage="A user with that email already exists.")

        emailValid, emailMsg = validateEmail(requestData.email)
        if not emailValid:
            return RegisterResponse(msg="Registration Unsuccesful.",
                                    emailMessage=emailMsg)
        passwordValid, passwordMsg = validatePassword(requestData.password)
        if not passwordValid:
            return RegisterResponse(msg="Registration Unsuccessful.",
                                    passwordMessage=passwordMsg)

        passwordSalt = pyBcrypt.gensalt().decode("utf-8")
        seasonedPassword = f"{requestData.password}{passwordSalt}"
        hashedPassword = bcrypt.generate_password_hash(seasonedPassword)

        user = User(username=requestData.username, email=requestData.email,
                    password=hashedPassword, passwordSalt=passwordSalt)
        user.save()

        sendEmail(mail, subject=CONFIRM_ACCOUNT_SUBJECT, recipients=[user.email],
                  msg=confirmAccountMessageTemplate(user.getConfirmationToken))

        accessToken = create_access_token(identity=user)
        refreshToken = create_refresh_token(identity=user)
        flaskResponse = jsonify(RegisterResponse(msg="You have been registered succesfully.",
                                                 accessToken=accessToken))
        set_refresh_cookies(flaskResponse, refreshToken)
        
        return flaskResponse
