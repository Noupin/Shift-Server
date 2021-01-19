#pylint: disable=C0103, C0301
"""
Routes for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
import os
import json
import tensorflow as tf
from flask import Blueprint, request, current_app
from flask_login import login_required, current_user

#First Party Imports
from src.api.inference.tasks import shift
from src.DataModels.MongoDB.User import User
from src.DataModels.MongoDB.Shift import Shift as ShiftDataModel
from src.DataModels.JSON.InferenceRequest import InferenceRequest


inferenceBP = Blueprint('inference', __name__)


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
            tf.keras.models.load_model(current_app.config["SHIFT_MODELS_FOLDER"], requestData.shiftUUID, "maskDecoder")
        except OSError:
            return {'msg': "That model does not exist"}

    shift.delay(requestData)

    return {'msg': f"Inferencing as {current_user}"}


@inferenceBP.route("/inferenceStatus", methods=["GET"])
@login_required
def inferenceStatus() -> dict:
    """
    The status of the current inferencing task.

    Returns:
        dict: A response with the status of the inferencing.
    """

    try:
        status = current_app.config["SHIFT_GLOBALS"].job.status

        return {'msg': f"The status is {status}"}

    except AttributeError:
        return {'msg': "There are currently no jobs"}
