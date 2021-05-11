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
from src.DataModels.Response.FeaturedShiftsResponse import (FeaturedShiftsResponse,
                                                            FeaturedShiftsResponseDescription)


class FeaturedShifts(MethodResource, Resource):

    @marshal_with(FeaturedShiftsResponse,
                  description=FeaturedShiftsResponseDescription)
    @doc(description="""
         The featured shifts to display on the home page.""")
    def get(self) -> dict:
        userShifts = Shift.objects().limit(2)
        userShiftsJSON: List[dict] = [json.loads(x.to_json()) for x in userShifts]

        return {"shifts": userShiftsJSON}
