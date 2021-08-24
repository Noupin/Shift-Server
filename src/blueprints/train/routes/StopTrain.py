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
from src import db
from src.constants import AUTHORIZATION_TAG
from src.models.SQL.TrainWorker import TrainWorker
from src.models.DataModelAdapter import DataModelAdapter
from src.models.Request.TrainRequest import TrainRequest
from src.models.Request.TrainRequest import (TrainRequest,
                                                 TrainRequestDescription)
from src.decorators.confirmationRequired import confirmationRequired
from src.utils.validators import validateBaseTrainRequest, validateShiftTitle
from src.models.Response.StopTrainResponse import (StopTrainResponse,
                                                       StopTrainResponseDescription)


class StopTrain(MethodResource, Resource):

    @use_kwargs(TrainRequest.Schema(),
                description=TrainRequestDescription)
    @marshal_with(StopTrainResponse.Schema(),
                  description=StopTrainResponseDescription)
    @doc(description="""Stop the training with the UUID of the shift model being \
trained.""", tags=["Train"], operationId="stopTrain", security=AUTHORIZATION_TAG)
    @jwt_required()
    @confirmationRequired
    def post(self, requestData: TrainRequest) -> dict:
        requestError = validateBaseTrainRequest(requestData)
        if isinstance(requestError, str):
            return StopTrainResponse(msg=requestError)
        del requestError
        
        if not validateShiftTitle(requestData.shiftTitle):
            return StopTrainResponse(msg="That is not a valid Shift title.") 

        requestData = DataModelAdapter(requestData)

        try:
            worker: TrainWorker = TrainWorker.query.filter_by(shiftUUID=requestData.getModel().shiftUUID).first()
        except Exception:
            return StopTrainResponse(msg="That training worker does not exist")
        worker.training = False
        worker.imagesUpdated = False
        db.session.commit()

        return StopTrainResponse(msg="Stop signal sent!")
