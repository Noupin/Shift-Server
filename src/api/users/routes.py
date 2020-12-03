#pylint: disable=C0103, C0301
"""
Routes for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
import jwt
import datetime
from flask import Blueprint, request, make_response
from flask_jwt_extended import create_access_token


users = Blueprint('users', __name__)


@users.route('/login', methods=["POST"])
def login():
    """
    The login for the user and distributes the JWT.

    Returns:
        JSON: A JWT token for future authorization.
    """

    if not request.is_json:
        return {"msg": "Missing JSON in request"}

    auth = request.get_json()

    if not auth["username"]:
        return {"msg": "Missing username"}
    if not auth["password"]:
        return {"msg": "Missing password"}

    if auth["username"] != 'Noupin' or auth["password"] != 'pass':
        return {"msg": "Username or Password incorrect"}
    
    token = create_access_token(identity=auth['username'], expires_delta=datetime.timedelta(seconds=10))
    return {'jwt' : token}
    
    return make_response("Could not verify!", 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})
