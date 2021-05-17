#pylint: disable=C0103, C0301
"""
Featured endpoint for the Users part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
import json
from typing import List
from flask_restful import Resource
from flask_apispec import marshal_with
from flask_apispec.annotations import doc
from flask_apispec.views import MethodResource

#First Party Imports
from src.DataModels.MongoDB.Shift import Shift
from src.DataModels.Response.PopularShiftsResponse import (PopularShiftsResponse,
                                                           PopularShiftsResponseDescription)


class PopularShifts(MethodResource, Resource):

    @marshal_with(PopularShiftsResponse,
                  description=PopularShiftsResponseDescription)
    @doc(description="""The popular shifts to display on the home page.""", tags=["FPN"],
operationId="popular")
    def get(self) -> dict:
        popularShifts = Shift.objects().limit(10)
        popularShiftsJSON: List[dict] = [json.loads(x.to_json()) for x in popularShifts]

        return PopularShiftsResponse().dump(dict(shifts=popularShiftsJSON))
