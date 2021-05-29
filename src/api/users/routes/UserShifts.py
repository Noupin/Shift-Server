#pylint: disable=C0103, C0301
"""
Shifts endpoint for the Users part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
import json
from typing import List
from flask_restful import Resource
from flask_apispec import marshal_with, doc
from flask_apispec.views import MethodResource
from flask_login import current_user, login_required

#First Party Imports
from src.DataModels.MongoDB.User import User
from src.DataModels.MongoDB.Shift import Shift
from src.variables.constants import SECURITY_TAG
from src.DataModels.Response.UserShiftsResponse import (UserShiftsResponse,
                                                        UserShiftsResponseDescription)


class UserShifts(MethodResource, Resource):
    decorators = [login_required]

    @marshal_with(UserShiftsResponse,
                  description=UserShiftsResponseDescription)
    @doc(description="""The users shifts to display the users account page.""", tags=["User"],
operationId="userShifts", security=SECURITY_TAG)
    def get(self) -> dict:
        user = User.objects(id=current_user.id)
        userShifts = Shift.objects(author__in=user)
        userShiftsJSON: List[dict] = [json.loads(x.to_json()) for x in userShifts]

        return {"shifts": userShiftsJSON}
