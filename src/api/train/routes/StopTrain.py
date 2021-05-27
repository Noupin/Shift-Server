#pylint: disable=C0103, C0301
"""
Stop Training endpoint for the Train part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from src.DataModels.Request.TrainRequest import TrainRequest
from flask import request
from flask_restful import Resource
from flask_login import login_required
from flask_apispec.annotations import doc
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, use_kwargs

#First Party Imports
from src.variables.constants import SECURITY_TAG
from src.utils.validators import validateBaseTrainRequest
from src.DataModels.MongoDB.TrainWorker import TrainWorker
from src.DataModels.DataModelAdapter import DataModelAdapter
from src.DataModels.Request.TrainRequest import (TrainRequest,
                                                 TrainRequestDescription)
from src.DataModels.Response.StopTrainResponse import (StopTrainResponse,
                                                       StopTrainResponseDescription)


class StopTrain(MethodResource, Resource):
    decorators = [login_required]

    @use_kwargs(TrainRequest.Schema(),
                description=TrainRequestDescription)
    @marshal_with(StopTrainResponse.Schema(),
                  description=StopTrainResponseDescription)
    @doc(description="""Stop the training with the UUID of the shift model being \
trained.""", tags=["Train"], operationId="stopTrain", security=SECURITY_TAG)
    def post(self, requestData: TrainRequest) -> dict:
        requestError = validateBaseTrainRequest(request)
        if isinstance(requestError, dict):
            return requestError

        requestData = DataModelAdapter(requestData)

        try:
            worker: TrainWorker = TrainWorker.objects.get(shiftUUID=requestData.getModel().shiftUUID)
        except Exception as e:
            return {"msg": "That training worker does not exist"}
        worker.update(set__training=False, set__imagesUpdated=False)

        return {'msg': "Stop signal sent!"}
