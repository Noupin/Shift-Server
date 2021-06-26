#pylint: disable=C0103, C0301
"""
New endpoint for the Users part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from typing import List
from flask_restful import Resource
from flask_apispec import marshal_with, doc
from flask_apispec.views import MethodResource

#First Party Imports
from src.DataModels.MongoDB.Shift import Shift
from src.DataModels.Marshmallow.Shift import ShiftSchema
from src.DataModels.Response.NewShiftsResponse import (NewShiftsResponse,
                                                       NewShiftsResponseDescription)


class NewShifts(MethodResource, Resource):

    @marshal_with(NewShiftsResponse,
                  description=NewShiftsResponseDescription)
    @doc(description="""The new shifts to display on the home page.""", tags=["Category"],
operationId="new")
    def get(self) -> dict:
        newShifts = Shift.objects().limit(10)
        newShiftsJSON: List[ShiftSchema] = [ShiftSchema().dump(x) for x in newShifts]

        return NewShiftsResponse().dump(dict(shifts=newShiftsJSON))
