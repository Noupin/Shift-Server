#pylint: disable=C0103, C0301
"""
Inference Status endpoint for the Inference part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from flask_restful import Resource
from celery.result import AsyncResult
from flask_jwt_extended import jwt_required
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, use_kwargs, doc

#First Party Import
from src.run import celery
from src.constants import AUTHORIZATION_TAG
from src.models.DataModelAdapter import DataModelAdapter
from src.models.SQL.Shift import Shift as ShiftDataModel
from src.utils.validators import validateInferenceRequest
from src.models.SQL.InferenceWorker import InferenceWorker
from src.decorators.confirmationRequired import confirmationRequired
from src.models.Request.InferenceRequest import (InferenceRequest,
                                                     InferenceRequestDescription)
from src.models.Response.InferenceStatusResponse import (InferenceStatusResponse,
                                                             InferenceStatusResponseDescription)


class InferenceStatus(MethodResource, Resource):

    @use_kwargs(InferenceRequest.Schema(),
                description=InferenceRequestDescription)
    @marshal_with(InferenceStatusResponse.Schema(),
                  description=InferenceStatusResponseDescription)
    @doc(description="""The status of the current shift model while inferencing on the \
original media and whether or not it has stopped inferencing.""", tags=["Inference"],
operationId="inferenceStatus", security=AUTHORIZATION_TAG)
    @jwt_required()
    @confirmationRequired
    def post(self, requestData: InferenceRequest):
        requestError = validateInferenceRequest(requestData)
        if isinstance(requestData, str):
            return InferenceStatusResponse(msg=requestError, stopped=False)
        del requestError
        
        requestModel = DataModelAdapter(requestData)

        try:
            worker: InferenceWorker = InferenceWorker.query.filter_by(shiftUUID=requestModel.getModel().shiftUUID).first()
        except Exception:
            return InferenceStatusResponse(msg="That inference worker does not exist", stopped=True)
        
        try:
            mongoShift: ShiftDataModel = ShiftDataModel.query.filter_by(uuid=requestModel.getModel().shiftUUID).first()
        except Exception:
            if requestModel.getModel().training:
                return InferenceStatusResponse(msg="A shift does not exist for the given UUID", stopped=True)

        job = AsyncResult(id=worker.workerID, backend=celery._get_backend())

        try:
            status = job.status

            if status == "SUCCESS":
                worker.delete()
                if requestModel.getModel().training:
                    return InferenceStatusResponse(msg="Shifting completed", stopped=True,
                                                   mediaFilename=mongoShift.mediaFilename,
                                                   baseMediaFilename=mongoShift.baseMediaFilename,
                                                   maskMediaFilename=mongoShift.maskMediaFilename)
                else:
                    return InferenceStatusResponse(msg="Shifting completed", stopped=True,
                                                   mediaFilename=worker.mediaFilename,
                                                   baseMediaFilename=worker.baseMediaFilename)

            elif status == "FAILURE":
                worker.delete()
                
                return InferenceStatusResponse(msg="The shifting task failed.", stopped=True)

            return InferenceStatusResponse(msg=f"The status is {status}", stopped=False)

        except AttributeError:
            return InferenceStatusResponse(msg="There are currently no jobs", stopped=True)
