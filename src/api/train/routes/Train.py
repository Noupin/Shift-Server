#pylint: disable=C0103, C0301
"""
Train endpoint for the Train part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
import os
import mongoengine
import tensorflow as tf
from flask import current_app
from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, use_kwargs, doc
from flask_jwt_extended import current_user, jwt_required

#First Party Imports
from src.api.train.tasks import trainShift
from src.variables.constants import (SHIFT_PATH,
                                     AUTHORIZATION_TAG)
from src.utils.validators import validateBaseTrainRequest, validateShiftTitle
from src.DataModels.MongoDB.TrainWorker import TrainWorker
from src.DataModels.DataModelAdapter import DataModelAdapter
from src.DataModels.Request.TrainRequest import (TrainRequest,
                                                 TrainRequestDescription)
from src.DataModels.Response.TrainResponse import (TrainResponse,
                                                   TrainResponseDescription)


class Train(MethodResource, Resource):

    @use_kwargs(TrainRequest.Schema(),
                description=TrainRequestDescription)
    @marshal_with(TrainResponse.Schema(),
                  description=TrainResponseDescription)
    @doc(description="""Given training data Shift specializes a model for the \
training data. Yeilds more relaisitic results than just an inference though it \
takes longer.""", tags=["Train"], operationId="train", security=AUTHORIZATION_TAG)
    @jwt_required()
    def post(self, requestData: TrainRequest) -> dict:
        requestError = validateBaseTrainRequest(requestData)
        if isinstance(requestError, str):
            return TrainResponse(msg=requestError)
        del requestError
        
        if not validateShiftTitle(requestData.shiftTitle):
            return TrainResponse(msg="That is not a valid Shift title.")
        
        if not current_user.canTrain:
            return TrainResponse(msg="You do not have access to train a Shift.")

        requestData = DataModelAdapter(requestData)

        if requestData.getModel().prebuiltShiftModel:
            try:
                tf.keras.models.load_model(os.path.join(current_app.root_path, SHIFT_PATH,
                                        requestData.getModel().prebuiltShiftModel, "encoder"))
                tf.keras.models.load_model(os.path.join(current_app.root_path, SHIFT_PATH,
                                        requestData.getModel().prebuiltShiftModel, "baseDecoder"))
            except OSError:
                return TrainResponse(msg="That model does not exist")

        worker = TrainWorker(shiftUUID=requestData.getModel().shiftUUID, training=True, inferencing=False)
        try:
            worker.save()
        except mongoengine.errors.NotUniqueError:
            return TrainResponse(msg="That AI is already training.")

        job = trainShift.delay(requestData.getSerializable(), str(current_user.id))
        worker.update(set__workerID=job.id)

        return TrainResponse(msg=f"Training as {current_user.username}")
