#pylint: disable=C0103, C0301
"""
Featured endpoint for the Users part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from flask_restful import Resource
from flask_apispec import marshal_with, doc
from flask_apispec.views import MethodResource
from src.DataModels.Marshmallow.Shift import ShiftSchema

#First Party Imports
from src.DataModels.MongoDB.Shift import Shift
from src.DataModels.MongoDB.Featured import Featured
from src.DataModels.Response.FeaturedShiftsResponse import (FeaturedShiftsResponse,
                                                            FeaturedShiftsResponseDescription)


class FeaturedShifts(MethodResource, Resource):

    @marshal_with(FeaturedShiftsResponse,
                  description=FeaturedShiftsResponseDescription)
    @doc(description="""The featured shifts to display on the home page.""", tags=["FPN"],
operationId="featured")
    def get(self) -> dict:
        featuredShiftUUIDs = Featured.objects().values_list('uuid')
        featuredShifts = []
        for uuid in featuredShiftUUIDs:
            shift = Shift.objects(uuid=uuid).first()
            featuredShifts.append(ShiftSchema().dump(shift))

        return FeaturedShiftsResponse().load(dict(shifts=featuredShifts))
