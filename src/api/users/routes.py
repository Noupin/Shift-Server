#pylint: disable=C0103, C0301
"""
Routes for the Users part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
import json
from typing import List
from flask import Blueprint, request, make_response, jsonify
from flask_login import login_user, logout_user, current_user, login_required

#First Party Imports
from src import bcrypt, login_manager
from src.DataModels.MongoDB.User import User
from src.DataModels.MongoDB.Shift import Shift
from src.utils.validators import validateEmail, validatePassword


users = Blueprint('users', __name__)


@login_manager.unauthorized_handler
def unauthorized() -> dict:
    """
    The unauthorized endpoint for the Shift app.

    Returns:
        dict: The msg telling the user they are not authorized
    """

    return {"msg": "You are not logged in and don't have access"}


@users.route("/register", methods=["POST"])
def register() -> dict:
    """
    The regitration for the user

    Returns:
        JSON: A JSON with a success or failure msg.
    """

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
    login_user(user, remember=True)
    
    return {"msg": "You have been registered succesfully"}


@users.route('/login', methods=["POST"])
def login() -> dict:
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


@users.route('/logout')
@login_required
def logout() -> dict:
    """
    The logout for the user.

    Returns:
        JSON: A JSON with a msg.
    """

    username = current_user.username
    logout_user()

    return {"msg": f"Logout Successful as {username}"}


@users.route('/profile')
@login_required
def profile() -> dict:
    """
    The users profile to display the on users the account page

    Returns:
        JSON: A JSON with the users profile to display on the users account page
    """

    userJSON = User.objects(id=current_user.id).first()

    return {"profile": userJSON}


@users.route('/shifts')
@login_required
def shifts() -> dict:
    """
    The users shifts to display the users account page

    Returns:
        JSON: A JSON with the users shifts to display on the users account page
    """

    userShifts = Shift.objects(userID=current_user.id)
    userShiftsJSON: List[dict] = [json.loads(x.to_json()) for x in userShifts]

    return {"shifts": userShiftsJSON}


@users.route('/isAuthenticated', methods=["GET"])
def isAuthenticated() -> dict:
    """
    Whether the user is logged in currently or not

    Returns:
        dict: A bool of whether the user is currently logged in
    """

    if current_user.is_authenticated:
        return {'authenticated': True}

    return {'authenticated': False}
