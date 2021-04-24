#pylint: disable=C0103, C0301
"""
Routes for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from logging import error
import os
import json
from flask.helpers import send_from_directory
import mongoengine
import tensorflow as tf
from typing import Union
from celery.result import AsyncResult
from flask_login import login_required, current_user
from flask import Blueprint, request, current_app, send_file

#First Party Imports
from src.run import celery
from src.api.inference.tasks import shiftMedia
from src.DataModels.DataModelAdapter import DataModelAdapter
from src.DataModels.JSON.InferenceRequest import InferenceRequest
from src.DataModels.MongoDB.InferenceWorker import InferenceWorker


inferenceBP = Blueprint('inference', __name__)

def validateInferenceRequest() -> Union[InferenceRequest, dict]:
    """
    Vialidates the inference request

    Returns:
        Union[TrainRequest, dict]: The inference request data or the error to send
    """

    if not request.is_json:
        return {'msg': "Your inference request had no JSON payload"}

    try:
        requestData: InferenceRequest = json.loads(json.dumps(request.get_json()), object_hook=lambda d: InferenceRequest(**d))
    except ValueError:
        return {"msg": "Not all fields for the InferenceRequest object were POSTed"}
    except TypeError:
        return {"msg": "Not all fields for the InferenceRequest object were POSTed"}

    if requestData.shiftUUID is None or requestData.shiftUUID is "":
        return {'msg': "Your inference request had no shiftUUID"}

    if requestData.usePTM is None:
        return {'msg': "Your inference request had not indication to use the prebuilt model or not"}

    if requestData.prebuiltShiftModel:
        try:
            tf.keras.models.load_model(os.path.join(current_app.config["SHIFT_MODELS_FOLDER"],
                                       requestData.prebuiltShiftModel, "encoder"))
            tf.keras.models.load_model(os.path.join(current_app.config["SHIFT_MODELS_FOLDER"],
                                       requestData.prebuiltShiftModel, "baseDecoder"))
            tf.keras.models.load_model(os.path.join(current_app.config["SHIFT_MODELS_FOLDER"],
                                       requestData.shiftUUID, "maskDecoder"))
        except OSError:
            return {'msg': "That model does not exist"}
    
    return requestData


@inferenceBP.route("/inference", methods=["POST"])
@login_required
def shift() -> dict:
    """
    Inferenceing based on a specialized pretrained model(PTM) where, the input is
    the face to be put on the media and inferenced with PTM. Alternativley inferencing
    with a given base video and shift face with a non specialized PTM.

    Returns:
        Shifted Media: The media that has been shifted by the pretrained model.
    """

    requestData = validateInferenceRequest()
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


@inferenceBP.route("/inferenceStatus", methods=["POST"])
@login_required
def inferenceStatus() -> dict:
    """
    The status of the current inferencing task.

    Returns:
        dict: A response with the status of the inferencing.
    """

    requestData = validateInferenceRequest()
    if isinstance(requestData, dict):
        return requestData
    requestData = DataModelAdapter(requestData)

    try:
        worker: InferenceWorker = InferenceWorker.objects.get(shiftUUID=requestData.getModel().shiftUUID)
    except Exception as e:
        return {"msg": "That inference worker does not exist", 'stopped': True}

    job = AsyncResult(id=worker.workerID, backend=celery._get_backend())

    try:
        status = job.status

        if status == "SUCCESS":
            worker.delete()
            return {'msg': "Shifting completed", 'stopped': True}

        elif status == "FAILURE":
            worker.delete()

            return {'msg': 'The shifting task failed.', 'stopped': True}

        return {'msg': f"The status is {status}", 'stopped': False}

    except AttributeError:
        return {'msg': "There are currently no jobs", 'stopped': True}
