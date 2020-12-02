#pylint: disable=C0103, C0301
"""
Routes for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from flask import Blueprint

#First Party Imports
from src import PRIVATE_KEY


users = Blueprint('users', __name__)


@users.route('/login', methods=["POST"])
def login():
    """
    The login for the user and distributes the JWT.

    Returns:
        JSON: A JWT token for future authorization.
    """

    data = flask.request.get_json()

    if data['username'] and data['password']:
        token = jwt.encode({'username' : data['username'],
                            'claims': ['Shift', 'Forge'],
                            'exp' : (datetime.datetime.utcnow()+datetime.timedelta(seconds=30))},
                           PRIVATE_KEY,
                           algorithm='RS256').decode('utf-8')

        return {'jwt' : token}
    
    return "Login Invalid.", 403