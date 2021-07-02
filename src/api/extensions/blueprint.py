#pylint: disable=C0103, C0301
"""
Routes for the Shift webapp
"""
__author__ = "Noupin"

#First Party Imports
from src import loginManager


@loginManager.unauthorized_handler
def unauthorized() -> dict:
    """
    The unauthorized endpoint for the Shift app.

    Returns:
        dict: The msg telling the user they are not authorized
    """

    return {"msg": "You are not logged in and don't have access"}