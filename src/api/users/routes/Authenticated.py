#pylint: disable=C0103, C0301
"""
Authentication endpoint for the Users part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from flask.views import MethodView
from flask_login import current_user


class Authenticated(MethodView):

    @staticmethod
    def get() -> dict:
        """
        Whether the user is logged in currently or not

        Returns:
            dict: A bool of whether the user is currently logged in
        """

        if current_user.is_authenticated:
            return {'authenticated': True}

        return {'authenticated': False}
