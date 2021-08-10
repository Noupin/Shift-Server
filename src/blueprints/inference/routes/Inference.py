#pylint: disable=C0103, C0301
"""
Inference endpoint for the Inference part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, use_kwargs, doc
from flask_jwt_extended import jwt_required, current_user

#First Party Imports
from src import db
from src.constants import AUTHORIZATION_TAG
from src.blueprints.inference.tasks import shiftMedia
from src.utils.validators import validateInferenceRequest
from src.models.DataModelAdapter import DataModelAdapter
from src.models.SQL.InferenceWorker import InferenceWorker
from src.decorators.confirmationRequired import confirmationRequired
from src.models.Request.InferenceRequest import (InferenceRequest,
                                                     InferenceRequestDescription)
from src.models.Response.InferenceResponse import (InferenceResponse,
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
    @confirmationRequired
    def post(self, requestData: InferenceRequest) -> dict:
        requestError = validateInferenceRequest(requestData)
        if isinstance(requestError, str):
            return InferenceResponse(msg=requestError)

        requestModel = DataModelAdapter(requestData)

        worker = InferenceWorker(shiftUUID=requestModel.getModel().shiftUUID)
        try:
            db.session.add(worker)
            db.session.commit()
        except Exception:
            return InferenceResponse(msg="That media is already being shifted.")

        job = shiftMedia.delay(requestModel.getSerializable())
        worker.workerID = job.id
        db.session.commit()

        return InferenceResponse(msg=f"Shifting as {current_user.username}")
