#pylint: disable=C0103, C0301
"""
Inference Status endpoint for the Inference part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from flask import request
from flask_restful import Resource
from celery.result import AsyncResult
from marshmallow import Schema, fields
from flask_apispec import marshal_with
from flask_apispec.views import MethodResource
from flask_login import login_required

#First Party Import
from src.run import celery
from src.utils.validators import validateInferenceRequest
from src.DataModels.DataModelAdapter import DataModelAdapter
from src.DataModels.MongoDB.Shift import Shift as ShiftDataModel
from src.DataModels.MongoDB.InferenceWorker import InferenceWorker


class InferenceStatusResponse(Schema):
    msg = fields.String(default="The status is status")
    stopped = fields.Boolean()
    imagePath = fields.String()
    

class InferenceStatus(MethodResource, Resource):
    decorators = [login_required]

    @marshal_with(InferenceStatusResponse)
    def post(self) -> dict:
        """
        The status of the current inferencing task.
        """

        requestData = validateInferenceRequest(request)
        if isinstance(requestData, dict):
            return requestData
        requestData = DataModelAdapter(requestData)

        try:
            worker: InferenceWorker = InferenceWorker.objects.get(shiftUUID=requestData.getModel().shiftUUID)
            mongoShift: ShiftDataModel = ShiftDataModel.objects.get(uuid=requestData.getModel().shiftUUID)
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
