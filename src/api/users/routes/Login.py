#pylint: disable=C0103, C0301
"""
Login endpoint for the Users part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from flask import request
from flask.views import MethodView
from flask_login import login_user, current_user

#First Party Imports
from src import bcrypt
from src.DataModels.MongoDB.User import User


class Login(MethodView):

    @staticmethod
    def post() -> dict:
        """
        The login for the user.

        Returns:
            JSON: A JSON with a success or failure msg.
        """

        if current_user.is_authenticated:
            return {'msg': "You are already logged in"}
        
        if not request.is_json:
            return {'msg': "Your login had no JSON payload"}
        
        requestData = request.get_json()
        if not requestData['usernameOrEmail']:
            return {'msg': "Username or Email missing"}
        
        if User.objects(email=requestData["usernameOrEmail"]).first():
            user = User.objects(email=requestData["usernameOrEmail"]).first()
        elif User.objects(username=requestData["usernameOrEmail"]).first():
            user = User.objects(username=requestData["usernameOrEmail"]).first()
        else:
            return {'msg': "Username or Email incorrect"}

        if bcrypt.check_password_hash(user.password, requestData["password"]):
            login_user(user, remember=requestData['remember'])
        else:
            return {'msg': 'Login unsuccesful, password incorrect'}

        return {'msg': "Login success."}
