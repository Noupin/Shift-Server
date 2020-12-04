#pylint: disable=C0103, C0301
"""
Routes for the Users part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
import jwt
import datetime
from flask import Blueprint, request, make_response, jsonify
from flask_login import login_user, logout_user, current_user

#First Party Imports
from src import bcrypt
from src.models import User, Shift


users = Blueprint('users', __name__)


@users.route("/register", methods=["POST"])
def register():
    if current_user.is_authenticated:
        return {'msg': "You already have an account"}
    
    if not request.is_json:
        return {'msg': "Your login had no JSON payload"}
    
    requestData = request.get_json()
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
    if requestData['email']:
        user = User.objects(email=requestData["email"]).first()
    elif requestData['username']:
        user = User.objects(username=requestData["username"]).first()
    else:
        return {'msg': "Username or Email incorrect"}

    if bcrypt.check_password_hash(user.password, requestData["password"]):
        login_user(user, remember=requestData['remember'])
    else:
        return {'msg': 'Login unsuccesful, password incorrect'}
    
    return {'msg': "Login success."}


@users.route('/logout', methods=["POST"])
def logout():
    """
    The logout for the user .

    Returns:
        str: A JSON with a msg.
    """

    logout_user()

    return {"msg": "Logout Successful"}
