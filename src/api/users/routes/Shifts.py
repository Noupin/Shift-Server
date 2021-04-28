#pylint: disable=C0103, C0301
"""
Shifts endpoint for the Users part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
import json
from typing import List
from flask.views import MethodView
from flask_login import current_user, login_required

#First Party Imports
from src.DataModels.MongoDB.Shift import Shift


class Shifts(MethodView):
    decorators = [login_required]

    @staticmethod
    def get() -> dict:
        """
        The users shifts to display the users account page

        Returns:
            JSON: A JSON with the users shifts to display on the users account page
        """

        userShifts = Shift.objects(userID=current_user.id)
        userShiftsJSON: List[dict] = [json.loads(x.to_json()) for x in userShifts]

        return {"shifts": userShiftsJSON}
