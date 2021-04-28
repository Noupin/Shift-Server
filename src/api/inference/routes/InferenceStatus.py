#pylint: disable=C0103, C0301
"""
Inference Status endpoint for the Inference part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from flask import request
from flask.views import MethodView
from celery.result import AsyncResult
from flask_login import login_required

#First Party Import
from src.run import celery
from src.utils.validators import validateInferenceRequest
from src.DataModels.DataModelAdapter import DataModelAdapter
from src.DataModels.MongoDB.Shift import Shift as ShiftDataModel
from src.DataModels.MongoDB.InferenceWorker import InferenceWorker



class InferenceStatus(MethodView):
    decorators = [login_required]

    @staticmethod
    def post() -> dict:
        """
        The status of the current inferencing task.

        Returns:
            dict: A response with the status of the inferencing.
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
