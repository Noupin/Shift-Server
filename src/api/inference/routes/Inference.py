#pylint: disable=C0103, C0301
"""
Inference endpoint for the Inference part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
import mongoengine
from flask import request
from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, use_kwargs, doc
from flask_jwt_extended import jwt_required, current_user

#First Party Imports
from src.api.inference.tasks import shiftMedia
from src.variables.constants import AUTHORIZATION_TAG
from src.utils.validators import validateInferenceRequest
from src.DataModels.DataModelAdapter import DataModelAdapter
from src.DataModels.MongoDB.InferenceWorker import InferenceWorker
from src.DataModels.Request.InferenceRequest import (InferenceRequest,
                                                     InferenceRequestDescription)
from src.DataModels.Response.InferenceResponse import (InferenceResponse,
                                                       InferenceResponseDescription)


class Inference(MethodResource, Resource):

    @use_kwargs(InferenceRequest.Schema(),
                description=InferenceRequestDescription)
    @marshal_with(InferenceResponse.Schema(),
                  description=InferenceResponseDescription)
    @doc(description="""Inferencing based on a specialized pretrained model(PTM) where, \
the input is the face to be put on the media and inferenced with PTM. Alternativley inferencing \
with a given base video and shift face with a non specialized PTM.""", tags=["Inference"],
operationId="inference", security=AUTHORIZATION_TAG)
    @jwt_required()
    def post(self, requestData: InferenceRequest) -> dict:
        requestError = validateInferenceRequest(requestData)
        if isinstance(requestError, str):
            return InferenceResponse(msg=requestError)

        requestModel = DataModelAdapter(requestData)

        worker = InferenceWorker(shiftUUID=requestModel.getModel().shiftUUID)
        try:
            worker.save()
        except mongoengine.errors.NotUniqueError:
            return InferenceResponse(msg="That media is already being shifted.")

        job = shiftMedia.delay(requestModel.getSerializable())
        worker.update(set__workerID=job.id)

        return InferenceResponse(msg=f"Shifting as {current_user.username}")
