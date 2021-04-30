#pylint: disable=C0103, C0301
"""
Train endpoint for the Train part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
import os
import mongoengine
import tensorflow as tf
from flask_restful import Resource
from flask import current_app, request
from marshmallow import Schema, fields
from flask_apispec import marshal_with
from flask_apispec.views import MethodResource
from flask_login import current_user, login_required

#First Party Imports
from src.api.train.tasks import trainShift
from src.variables.constants import SHIFT_PATH
from src.utils.validators import validateBaseTrainRequest
from src.DataModels.MongoDB.TrainWorker import TrainWorker
from src.DataModels.DataModelAdapter import DataModelAdapter


class TrainResponse(Schema):
    msg = fields.String()

class Train(MethodResource, Resource):
    decorators = [login_required]

    @marshal_with(TrainResponse)
    def post(self) -> dict:
        """
        Given training data Shift specializes a model for the training data. Yeilds
        more relaisitic results than just an inference though it takes longer.

        Request Body Arguments:
            shiftUUID (str): The UUID of the current shift training session
            usePTM (bool): Whether or not to use the pre-trained model to enhace shifting
            prebuiltShiftModel (str): The id of the prebuilt model to use or an empty
                                    string if not using a prebuilt model

        Returns:
            Shifted Media: The media that has been shifted by the specialized model.
        """

        requestData = validateBaseTrainRequest(request)
        if isinstance(requestData, dict):
            return requestData
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
