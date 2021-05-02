#pylint: disable=C0103, C0301
"""
Shifts endpoint for the Users part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
import json
from typing import List
from marshmallow import Schema, fields
from flask_restful import Resource
from flask_apispec import marshal_with
from flask_apispec.views import MethodResource
from flask_login import current_user, login_required

#First Party Imports
from src.DataModels.MongoDB.Shift import Shift
from src.DataModels.Marshmallow.Shift import ShiftSchema


class UserShiftsResponse(Schema):
    shifts = fields.List(fields.Nested(ShiftSchema))

class UserShifts(MethodResource, Resource):
    decorators = [login_required]

    @marshal_with(UserShiftsResponse)
    def get(self) -> dict:
        """
        The users shifts to display the users account page
        """

        userShifts = Shift.objects(userID=current_user.id)
        userShiftsJSON: List[dict] = [json.loads(x.to_json()) for x in userShifts]

        return {"shifts": userShiftsJSON}
