#pylint: disable=C0103, C0301
"""
Routes for the Users part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
import jwt
import datetime
from flask import Blueprint, request, make_response, jsonify
from flask_login import login_user, logout_user, current_user, login_required

#First Party Imports
from src import bcrypt
from src.DataModels.Shift import Shift
from src.DataModels.User import User
from src.utils.Validators import validateEmail, validatePassword


users = Blueprint('users', __name__)


@users.route("/register", methods=["POST"])
def register():
    if current_user.is_authenticated:
        return {'msg': "You're already logged in"}
    
    if not request.is_json:
        return {'msg': "Your login had no JSON payload"}
    
    requestData = request.get_json()

    if User.objects(username=requestData["username"]).first():
        return {'msg': "A user with that username already exists"}
    if User.objects(email=requestData["email"]).first():
        return {'msg': "A user with that email already exists"}

    emailValid, emailMsg = validateEmail(requestData["email"])
    if not emailValid:
        return {'msg': emailMsg}
    passwordValid, passwordMsg = validatePassword(requestData["password"])
    if not passwordValid:
        return {'msg': passwordMsg}

    hashed_password = bcrypt.generate_password_hash(requestData['password'])
    user = User(username=requestData['username'], email=requestData['email'], password=hashed_password)
    user.save()
    login_user(user, remember=requestData['remember'])
    
    return {"msg": "You have been registered succesfully"}


@users.route('/login', methods=["POST"])
def login():
    """
    The login for the user.

    Returns:
        str: A JSON with a msg.
    """

    if current_user.is_authenticated:
        return {'msg': "You are already logged in"}
    
    if not request.is_json:
        return {'msg': "Your login had no JSON payload"}
    
    requestData = request.get_json()
    if not requestData['usernameOrEmail']:
        return {'msg': "Username or Email incorrect"}
    
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


@users.route('/logout')
@login_required
def logout():
    """
    The logout for the user.

    Returns:
        str: A JSON with a msg.
    """

    username = current_user.username
    logout_user()

    return {"msg": f"Logout Successful as {username}"}
