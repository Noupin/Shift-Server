#pylint: disable=C0103, C0301
"""
Stop Training endpoint for the Train part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, use_kwargs, doc

#First Party Imports
from src.variables.constants import AUTHORIZATION_TAG
from src.DataModels.MongoDB.TrainWorker import TrainWorker
from src.DataModels.DataModelAdapter import DataModelAdapter
from src.DataModels.Request.TrainRequest import TrainRequest
from src.DataModels.Request.TrainRequest import (TrainRequest,
                                                 TrainRequestDescription)
from src.utils.validators import validateBaseTrainRequest, validateShiftTitle
from src.DataModels.Response.StopTrainResponse import (StopTrainResponse,
                                                       StopTrainResponseDescription)


class StopTrain(MethodResource, Resource):

    @use_kwargs(TrainRequest.Schema(),
                description=TrainRequestDescription)
    @marshal_with(StopTrainResponse.Schema(),
                  description=StopTrainResponseDescription)
    @doc(description="""Stop the training with the UUID of the shift model being \
trained.""", tags=["Train"], operationId="stopTrain", security=AUTHORIZATION_TAG)
    @jwt_required()
    def post(self, requestData: TrainRequest) -> dict:
        requestError = validateBaseTrainRequest(requestData)
        if isinstance(requestError, str):
            return StopTrainResponse(msg=requestError)
        del requestError
        
        if not validateShiftTitle(requestData.shiftTitle):
            return StopTrainResponse(msg="That is not a valid Shift title.") 

        requestData = DataModelAdapter(requestData)

        try:
            worker: TrainWorker = TrainWorker.objects.get(shiftUUID=requestData.getModel().shiftUUID)
        except Exception:
            return StopTrainResponse(msg="That training worker does not exist")
        worker.update(set__training=False, set__imagesUpdated=False)

        return StopTrainResponse(msg="Stop signal sent!")
