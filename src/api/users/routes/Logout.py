#pylint: disable=C0103, C0301
"""
Logout endpoint for the Users part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from flask.views import MethodView
from flask_login import logout_user, current_user, login_required


class Logout(MethodView):
    decorators = [login_required]

    @staticmethod
    def get() -> dict:
        """
        The logout for the user.

        Returns:
            JSON: A JSON with a msg.
        """

        username = current_user.username
        logout_user()

        return {"msg": f"Logout Successful as {username}"}
