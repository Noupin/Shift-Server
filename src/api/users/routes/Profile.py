#pylint: disable=C0103, C0301
"""
Profile endpoint for the Users part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from flask.views import MethodView
from flask_login import current_user, login_required

#First Party Imports
from src.DataModels.MongoDB.User import User


class Profile(MethodView):
    decorators = [login_required]

    @staticmethod
    def get() -> dict:
        """
        The users profile to display the on users the account page

        Returns:
            JSON: A JSON with the users profile to display on the users account page
        """

        userJSON = User.objects(id=current_user.id).first()

        return {"profile": userJSON}
