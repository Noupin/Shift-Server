#pylint: disable=C0103, C0301
"""
Individual shift endpoint for the shift part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
import os
import shutil
from uuid import UUID
from flask.globals import current_app
from flask_restful import Resource
from flask_apispec import marshal_with, doc
from flask_apispec.views import MethodResource
from src.DataModels.Marshmallow.Shift import ShiftSchema

#First Party Imports
from src.variables.constants import IMAGE_PATH, SHIFT_PATH
from src.DataModels.MongoDB.Shift import Shift
from src.DataModels.Response.IndividualShiftGetResponse import (IndividualShiftGetResponse,
                                                                IndividualShiftGetResponseDescription)
from src.DataModels.Response.IndividualShiftDeleteResponse import (IndividualShiftDeleteResponse,
                                                                   IndividualShiftDeleteResponseDescription)


class IndividualShift(MethodResource, Resource):

    @marshal_with(IndividualShiftGetResponse,
                  description=IndividualShiftGetResponseDescription)
    @doc(description="""The queried shift""",
         tags=["Shift"], operationId="getIndivdualShift")
    def get(self, uuid: str) -> IndividualShiftGetResponse:
        try:
            shift: Shift = Shift.objects(uuid=UUID(uuid)).first()
        except ValueError:
            return IndividualShiftGetResponse()

        shiftModel: ShiftSchema = ShiftSchema().dump(shift)

        return IndividualShiftGetResponse().load(dict(shift=shiftModel))


    @marshal_with(IndividualShiftDeleteResponse,
                  description=IndividualShiftDeleteResponseDescription)
    @doc(description="""Deletes the queried shift.""",
         tags=["Shift"], operationId="deleteIndivdualShift")
    def delete(self, uuid: str) -> IndividualShiftDeleteResponse:
        try:
            shift: Shift = Shift.objects(uuid=UUID(uuid)).first()
        except ValueError:
            return IndividualShiftDeleteResponse().load(dict(msg="""Shift was not \
                deleted because it does not exist."""))

        title = shift.title
        
        shutil.rmtree(os.path.join(current_app.root_path, SHIFT_PATH, str(shift.uuid)))
        os.remove(os.path.join(current_app.root_path, IMAGE_PATH, shift.imagePath))
        shift.delete()
        
        return IndividualShiftDeleteResponse().load(dict(msg=f"Shift {title} deleted."))
