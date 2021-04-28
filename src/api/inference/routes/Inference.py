#pylint: disable=C0103, C0301
"""
Inference endpoint for the Inference part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
import mongoengine
from flask import request
from flask.views import MethodView
from flask_login import login_required, current_user

#First Party Imports
from src.api.inference.tasks import shiftMedia
from src.utils.validators import validateInferenceRequest
from src.DataModels.DataModelAdapter import DataModelAdapter
from src.DataModels.MongoDB.InferenceWorker import InferenceWorker


class Inference(MethodView):
    decorators = [login_required]

    @staticmethod
    def post() -> dict:
        """
        Inferenceing based on a specialized pretrained model(PTM) where, the input is
        the face to be put on the media and inferenced with PTM. Alternativley inferencing
        with a given base video and shift face with a non specialized PTM.

        Returns:
            Shifted Media: The media that has been shifted by the pretrained model.
        """

        requestData = validateInferenceRequest(request)
        if isinstance(requestData, dict):
            return requestData
        requestData = DataModelAdapter(requestData)

        worker = InferenceWorker(shiftUUID=requestData.getModel().shiftUUID)
        try:
            worker.save()
        except mongoengine.errors.NotUniqueError:
            return {'msg': "That media is already being shifted."}

        job = shiftMedia.delay(requestData.getSerializable())
        worker.update(set__workerID=job.id)

        return {'msg': f"Shifting as {current_user.username}"}