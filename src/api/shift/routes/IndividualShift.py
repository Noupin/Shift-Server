#pylint: disable=C0103, C0301
"""
Individual shift endpoint for the shift part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from uuid import UUID
from flask_restful import Resource
from flask_apispec import marshal_with, doc
from flask_apispec.views import MethodResource
from src.DataModels.Marshmallow.Shift import ShiftSchema

#First Party Imports
from src.DataModels.MongoDB.Shift import Shift
from src.DataModels.Response.IndividualShiftResponse import (IndividualShiftResponse,
                                                             IndividualShiftResponseDescription)


class IndividualShift(MethodResource, Resource):

    @marshal_with(IndividualShiftResponse,
                  description=IndividualShiftResponseDescription)
    @doc(description="""The queried shift""",
         tags=["Shift"], operationId="indivdualShift")
    def get(self, uuid: str) -> dict:
        try:
            shift: Shift = Shift.objects(uuid=UUID(uuid)).first()
        except ValueError:
            return IndividualShiftResponse()

        print("Here")
        shiftModel: ShiftSchema = ShiftSchema().dump(shift)

        return IndividualShiftResponse().load(dict(shift=shiftModel))
