#pylint: disable=C0103, C0301
"""
Train endpoint for the Train part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
import os
from src.DataModels.Marshmallow.User import UserSchema
import mongoengine
import tensorflow as tf
from flask_restful import Resource
from flask import current_app, request
from flask_apispec.views import MethodResource
from flask_login import current_user, login_required
from flask_apispec import marshal_with, use_kwargs, doc

#First Party Imports
from src.api.train.tasks import trainShift
from src.variables.constants import (SHIFT_PATH,
                                     SECURITY_TAG)
from src.utils.validators import validateBaseTrainRequest
from src.DataModels.MongoDB.TrainWorker import TrainWorker
from src.DataModels.DataModelAdapter import DataModelAdapter
from src.DataModels.Request.TrainRequest import (TrainRequest,
                                                 TrainRequestDescription)
from src.DataModels.Response.TrainResponse import (TrainResponse,
                                                   TrainResponseDescription)


class Train(MethodResource, Resource):
    decorators = [login_required]

    @use_kwargs(TrainRequest.Schema(),
                description=TrainRequestDescription)
    @marshal_with(TrainResponse.Schema(),
                  description=TrainResponseDescription)
    @doc(description="""Given training data Shift specializes a model for the \
training data. Yeilds more relaisitic results than just an inference though it \
takes longer.""", tags=["Train"], operationId="train", security=SECURITY_TAG)
    def post(self, requestData: TrainRequest) -> dict:
        requestError = validateBaseTrainRequest(request)
        if isinstance(requestError, dict):
            return requestError

        requestData = DataModelAdapter(requestData)

        if requestData.getModel().prebuiltShiftModel:
            try:
                tf.keras.models.load_model(os.path.join(current_app.root_path, SHIFT_PATH,
                                        requestData.getModel().prebuiltShiftModel, "encoder"))
                tf.keras.models.load_model(os.path.join(current_app.root_path, SHIFT_PATH,
                                        requestData.getModel().prebuiltShiftModel, "baseDecoder"))
            except OSError:
                return {'msg': "That model does not exist"}

        worker = TrainWorker(shiftUUID=requestData.getModel().shiftUUID, training=True, inferencing=False)
        try:
            worker.save()
        except mongoengine.errors.NotUniqueError:
            return {'msg': "That AI is already training."}

        job = trainShift.delay(requestData.getSerializable(), str(current_user.id))
        worker.update(set__workerID=job.id)

        return {'msg': f"Training as {current_user.username}"}
