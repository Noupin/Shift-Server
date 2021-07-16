#pylint: disable=C0103, C0301
"""
Popular endpoint for the Users part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from typing import List
from flask_restful import Resource
from flask_apispec import marshal_with, doc
from flask_apispec.views import MethodResource

#First Party Imports
from src.DataModels.MongoDB.Shift import Shift
from src.variables.constants import AMOUNT_OF_POPULAR
from src.DataModels.Marshmallow.Shift import ShiftSchema
from src.DataModels.Response.PopularShiftsResponse import (PopularShiftsResponse,
                                                           PopularShiftsResponseDescription)


class PopularShifts(MethodResource, Resource):

    @marshal_with(PopularShiftsResponse,
                  description=PopularShiftsResponseDescription)
    @doc(description="""The popular shifts to display on the home page.""", tags=["Category"],
operationId="popular")
    def get(self) -> dict:
        popularShifts = Shift.objects().order_by('-views').limit(AMOUNT_OF_POPULAR)
        popularShiftsJSON: List[ShiftSchema] = [ShiftSchema().dump(x) for x in popularShifts]

        return PopularShiftsResponse().dump(dict(shifts=popularShiftsJSON))
