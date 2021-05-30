#pylint: disable=C0103, C0301
"""
The endpointfor all public shifts from any user for the user part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from typing import List, Union
from flask_restful import Resource
from flask_apispec import marshal_with, doc
from flask_apispec.views import MethodResource
from src.DataModels.Marshmallow.Shift import ShiftSchema

#First Party Imports
from src.DataModels.MongoDB.User import User
from src.DataModels.MongoDB.Shift import Shift
from src.DataModels.Response.UserShiftsResponse import (UserShiftsResponse,
                                                        UserShiftsResponseDescription)


class UserShifts(MethodResource, Resource):
    
    @staticmethod
    def userExists(username: str) -> Union[User, dict]:
        try:
            return User.objects(username=username).first()
        except ValueError:
            return {}


    @marshal_with(UserShiftsResponse,
                  description=UserShiftsResponseDescription)
    @doc(description="""The shifts associated with the queried user.""",
         tags=["User"], operationId="userShifts")
    def get(self, username: str):
        user = self.userExists(username)
        if not isinstance(user, User):
            return UserShiftsResponse()

        userShifts = Shift.objects(author__in=[user])
        userShiftsJSON: List[ShiftSchema] = [ShiftSchema().dump(x) for x in userShifts]

        return UserShiftsResponse().load(dict(shifts=userShiftsJSON))