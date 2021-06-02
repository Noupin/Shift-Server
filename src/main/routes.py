#pylint: disable=C0103, C0301
"""
Routes for the Shift webapp
"""
__author__ = "Noupin"

#Third Party Imports
from flask import Blueprint
from flask.wrappers import Response

#First Party Imports
from src import login_manager


mainBP = Blueprint('main', __name__, static_folder="../static/build", static_url_path="/")


@mainBP.route('/*')
def index() -> Response:
    return mainBP.send_static_file('index.html')


'''@mainBP.app_errorhandler(404)
def error404(error) -> Response:
    return mainBP.send_static_file('index.html')'''


@login_manager.unauthorized_handler
def unauthorized() -> dict:
    """
    The unauthorized endpoint for the Shift app.

    Returns:
        dict: The msg telling the user they are not authorized
    """
    print("Not Logged In.")
    return {"msg": "You are not logged in and don't have access"}
