#pylint: disable=C0103, C0301
"""
Individual shift endpoint for the shift part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
import os
import shutil
from typing import Union
from uuid import UUID
from flask import current_app
from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask_login import login_required, current_user
from flask_apispec import marshal_with, doc, use_kwargs
from src.DataModels.Marshmallow.Shift import ShiftSchema

#First Party Imports
from src.utils.files import getMediaType
from src.DataModels.MongoDB.Shift import Shift
from src.variables.constants import IMAGE_PATH, VIDEO_PATH, SHIFT_PATH
from src.DataModels.Request.IndividualShiftPutRequest import (IndividualShiftPutRequest,
                                                              IndividualShiftPutRequestDescription)
from src.DataModels.Response.IndividualShiftGetResponse import (IndividualShiftGetResponse,
                                                                IndividualShiftGetResponseDescription)
from src.DataModels.Response.IndividualShiftPutResponse import (IndividualShiftPutResponse,
                                                                IndividualShiftPutResponseDescription)
from src.DataModels.Response.IndividualShiftDeleteResponse import (IndividualShiftDeleteResponse,
                                                                   IndividualShiftDeleteResponseDescription)


class IndividualShift(MethodResource, Resource):
    
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
         tags=["Shift"], operationId="deleteIndivdualShift")
    @login_required
    def delete(self, uuid: str):
        shift = self.shiftExists(uuid)
        if not isinstance(shift, Shift):
            return IndividualShiftDeleteResponse().load(dict(msg="""Shift was not \
deleted because it does not exist."""))

        if(current_user.id != shift.author.id):
            return IndividualShiftDeleteResponse().load(dict(msg="""You cannot \
delete a shift which you did not create."""))

        title = shift.title
        
        shutil.rmtree(os.path.join(current_app.root_path, SHIFT_PATH, str(shift.uuid)))
        if getMediaType(shift.mediaFilename) == "image":
            os.remove(os.path.join(current_app.root_path, IMAGE_PATH, shift.mediaFilename))
        elif getMediaType(shift.mediaFilename) == "video":
            os.remove(os.path.join(current_app.root_path, VIDEO_PATH, shift.mediaFilename))
        shift.delete()
        
        return IndividualShiftDeleteResponse().load(dict(msg=f"The Shift named: {title} has been deleted."))


    @use_kwargs(IndividualShiftPutRequest,
                description=IndividualShiftPutRequestDescription)
    @marshal_with(IndividualShiftPutResponse.Schema(),
                  description=IndividualShiftPutResponseDescription)
    @doc(description="""Updates/repalces the queried shift.""",
         tags=["Shift"], operationId="putIndivdualShift")
    @login_required
    def put(self, uuid, requestBody):
        shift = self.shiftExists(uuid)
        if not isinstance(shift, Shift):
            return IndividualShiftDeleteResponse().load(dict(msg="""Shift was not \
updated because it does not exist."""))

        return IndividualShiftPutResponse().load(dict(msg="Put Recieved"))