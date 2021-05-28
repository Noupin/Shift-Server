#pylint: disable=C0103, C0301
"""
Inference Status endpoint for the Inference part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from flask import request
from flask_restful import Resource
from celery.result import AsyncResult
from flask_login import login_required
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, use_kwargs, doc

#First Party Import
from src.run import celery
from src.variables.constants import SECURITY_TAG
from src.utils.validators import validateInferenceRequest
from src.DataModels.DataModelAdapter import DataModelAdapter
from src.DataModels.MongoDB.Shift import Shift as ShiftDataModel
from src.DataModels.MongoDB.InferenceWorker import InferenceWorker
from src.DataModels.Request.InferenceRequest import (InferenceRequest,
                                                     InferenceRequestDescription)
from src.DataModels.Response.InferenceStatusResponse import (InferenceStatusReponse,
                                                             InferenceStatusReponseDescription)


class InferenceStatus(MethodResource, Resource):
    decorators = [login_required]

    @use_kwargs(InferenceRequest.Schema(),
                description=InferenceRequestDescription)
    @marshal_with(InferenceStatusReponse.Schema(),
                  description=InferenceStatusReponseDescription)
    @doc(description="""The status of the current shift model while inferencing on the \
original media and whether or not it has stopped inferencing.""", tags=["Inference"],
operationId="inferenceStatus", security=SECURITY_TAG)
    def post(self, requestData: InferenceRequest):

        requestError = validateInferenceRequest(request)
        if isinstance(requestData, dict):
            return requestError
        requestModel = DataModelAdapter(requestData)

        try:
            worker: InferenceWorker = InferenceWorker.objects.get(shiftUUID=requestModel.getModel().shiftUUID)
            mongoShift: ShiftDataModel = ShiftDataModel.objects.get(uuid=requestModel.getModel().shiftUUID)
        except Exception as e:
            return {"msg": "That inference worker does not exist", 'stopped': True}

        job = AsyncResult(id=worker.workerID, backend=celery._get_backend())

        try:
            status = job.status

            if status == "SUCCESS":
                worker.delete()
                return {'msg': "Shifting completed", 'stopped': True, "imagePath": mongoShift.imagePath}

            elif status == "FAILURE":
                worker.delete()

                return {'msg': 'The shifting task failed.', 'stopped': True}

            return {'msg': f"The status is {status}", 'stopped': False}

        except AttributeError:
            return {'msg': "There are currently no jobs", 'stopped': True}
