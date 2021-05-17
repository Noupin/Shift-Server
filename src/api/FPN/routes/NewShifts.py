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
from src.DataModels.Response.NewShiftsResponse import (NewShiftsResponse,
                                                       NewShiftsResponseDescription)


class NewShifts(MethodResource, Resource):

    @marshal_with(NewShiftsResponse,
                  description=NewShiftsResponseDescription)
    @doc(description="""The new shifts to display on the home page.""", tags=["FPN"],
operationId="new")
    def get(self) -> dict:
        newShifts = Shift.objects().order_by('-views').limit(10)
        newShiftsJSON: List[dict] = [json.loads(x.to_json()) for x in newShifts]

        return NewShiftsResponse().dump(dict(shifts=newShiftsJSON))
