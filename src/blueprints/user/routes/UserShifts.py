#pylint: disable=C0103, C0301
"""
The endpointfor all public shifts from any user for the user part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from typing import List
from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs

#First Party Imports
from src.models.SQL.Shift import Shift
from src.constants import ITEMS_PER_PAGE
from src.models.Marshmallow.User import UserSchema
from src.models.Marshmallow.Shift import ShiftSchema
from src.models.Request.UserShiftsRequest import (UserShiftsRequest,
                                                      UserShiftsRequestDescription)
from src.models.Response.UserShiftsResponse import (UserShiftsResponse,
                                                        UserShiftsResponseDescription)


class UserShifts(MethodResource, Resource):

    @use_kwargs(UserShiftsRequest.Schema(), location='query',
                description=UserShiftsRequestDescription)
    @marshal_with(UserShiftsResponse,
                  description=UserShiftsResponseDescription)
    @doc(description="""The shifts associated with the queried user.""",
         tags=["User"], operationId="userShifts")
    def get(self, queryParams: UserShiftsRequest, username: str):
        user = UserSchema.getUserByUsername(username)
        if not user:
            return UserShiftsResponse()

        userShifts = Shift.query.filter_by(author__in=[user]).paginate(queryParams.page, ITEMS_PER_PAGE)
        userShiftsJSON: List[ShiftSchema] = [ShiftSchema().dump(x) for x in userShifts]

        return UserShiftsResponse().load(dict(shifts=userShiftsJSON))
