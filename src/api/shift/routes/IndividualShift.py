#pylint: disable=C0103, C0301
"""
Individual shift endpoint for the shift part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
import os
import shutil
from uuid import UUID
from typing import Union
from flask import current_app
from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask_login import login_required, current_user
from flask_apispec import marshal_with, doc, use_kwargs
from src.DataModels.Marshmallow.Shift import ShiftSchema

#First Party Imports
from src.utils.files import getMediaType
from src.DataModels.MongoDB.Shift import Shift
from src.variables.constants import IMAGE_PATH, USER_EDITABLE_SHIFT_FIELDS, VIDEO_PATH, SHIFT_PATH, SECURITY_TAG
from src.DataModels.Response.IndividualShiftGetResponse import (IndividualShiftGetResponse,
                                                                IndividualShiftGetResponseDescription)
from src.DataModels.Request.IndividualShiftPatchRequest import (IndividualShiftPatchRequest,
                                                                IndividualShiftPatchRequestDescription)
from src.DataModels.Response.IndividualShiftPatchResponse import (IndividualShiftPatchResponse,
                                                                  IndividualShiftPatchResponseDescription)
from src.DataModels.Response.IndividualShiftDeleteResponse import (IndividualShiftDeleteResponse,
                                                                   IndividualShiftDeleteResponseDescription)


class IndividualShift(MethodResource, Resource):
    
    @staticmethod
    def shiftExists(uuid: str) -> Union[Shift, dict]:
        try:
            return Shift.objects(uuid=UUID(uuid)).first()
        except ValueError:
            return {}


    @marshal_with(IndividualShiftGetResponse,
                  description=IndividualShiftGetResponseDescription)
    @doc(description="""The queried shift""",
         tags=["Shift"], operationId="getIndivdualShift")
    def get(self, uuid: str):
        shift = self.shiftExists(uuid)
        if not isinstance(shift, Shift):
            return IndividualShiftGetResponse()

        shiftModel: ShiftSchema = ShiftSchema().dump(shift)

        return IndividualShiftGetResponse().load(dict(shift=shiftModel))


    @marshal_with(IndividualShiftDeleteResponse.Schema(),
                  description=IndividualShiftDeleteResponseDescription)
    @doc(description="""Deletes the queried shift.""",
         tags=["Shift"], operationId="deleteIndivdualShift", security=SECURITY_TAG)
    @login_required
    def delete(self, uuid: str):
        shift = self.shiftExists(uuid)
        if not isinstance(shift, Shift):
            return IndividualShiftDeleteResponse(msg="""Shift was not \
deleted because it does not exist.""")

        if(current_user.id != shift.author.id):
            return IndividualShiftDeleteResponse(msg="""You cannot \
delete a shift which you did not create.""")

        title = shift.title
        
        shutil.rmtree(os.path.join(current_app.root_path, SHIFT_PATH, str(shift.uuid)))
        if getMediaType(shift.mediaFilename) == "image":
            os.remove(os.path.join(current_app.root_path, IMAGE_PATH, shift.mediaFilename))
        elif getMediaType(shift.mediaFilename) == "video":
            os.remove(os.path.join(current_app.root_path, VIDEO_PATH, shift.mediaFilename))
        shift.delete()
        
        return IndividualShiftDeleteResponse(msg=f"The Shift named: {title} has been deleted.")


    @use_kwargs(IndividualShiftPatchRequest.Schema(),
                description=IndividualShiftPatchRequestDescription)
    @marshal_with(IndividualShiftPatchResponse.Schema(),
                  description=IndividualShiftPatchResponseDescription)
    @doc(description="""Updates/modifies the queried shift.""",
         tags=["Shift"], operationId="patchIndivdualShift", security=SECURITY_TAG)
    @login_required
    def patch(self, requestBody: IndividualShiftPatchRequest, uuid: str):
        shift = self.shiftExists(uuid)
        if not isinstance(shift, Shift):
            return IndividualShiftPatchResponse(msg="""Shift was not \
updated because it does not exist.""")
            
        if(current_user.id != shift.author.id):
            return IndividualShiftPatchResponse(msg="""You cannot \
delete a shift which you did not create.""")

        queries = {}
        for field, value in requestBody.data.items():
            if field not in USER_EDITABLE_SHIFT_FIELDS:
                return IndividualShiftPatchResponse(msg="You are not allowed to change this field.")
            
            else:
                queries[f"set__{field}"] = value

        try:
            shift.update(**queries)
        except ValueError:
            return IndividualShiftPatchResponse(msg=f"The field you are changing is \
not the same type as the value you submitted"), 500
        except TypeError:
            return IndividualShiftPatchResponse(msg=f"The field you are changing is \
not the same type as the value you submitted"), 500

        return IndividualShiftPatchResponse(msg=f"The fields \
{[field for field, _ in requestBody.data.items()]} in the {shift.title} Shift have been modified.")
