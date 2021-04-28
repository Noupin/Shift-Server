#pylint: disable=C0103, C0301
"""
Stop Training endpoint for the Train part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from flask import request
from flask.views import MethodView
from flask_login import login_required

#First Party Imports
from src.utils.validators import validateBaseTrainRequest
from src.DataModels.MongoDB.TrainWorker import TrainWorker
from src.DataModels.DataModelAdapter import DataModelAdapter


class StopTrain(MethodView):
    decorators = [login_required]

    @staticmethod
    def post() -> dict:
        """
        Stop the training with the UUID of the shift model being trained.

        Returns:
            dict: A msg confirming the cancellation of the shift training.
        """

        requestData = validateBaseTrainRequest(request)
        if isinstance(requestData, dict):
            return requestData
        requestData = DataModelAdapter(requestData)

        try:
            worker: TrainWorker = TrainWorker.objects.get(shiftUUID=requestData.getModel().shiftUUID)
        except Exception as e:
            return {"msg": "That training worker does not exist"}
        worker.update(set__training=False, set__imagesUpdated=False)

        return {'msg': "Stop signal sent!"}
