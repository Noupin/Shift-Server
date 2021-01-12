#pylint: disable=C0103, C0301
"""
The training route for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
import os
import json
import tensorflow as tf
from flask import Blueprint, request, current_app
from flask_login import login_required, current_user

#First Party Imports
from src.DataModels.MongoDB.User import User
from src.DataModels.JSON.TrainRequest import TrainRequest
from src.DataModels.MongoDB.Shift import Shift as ShiftDataModel


train = Blueprint('train', __name__)


@train.route("/train", methods=["POST"])
@login_required
def trainShift() -> dict:
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

    if not request.is_json:
        return {'msg': "Your train request had no JSON payload"}

    try:
        requestData: TrainRequest = json.loads(json.dumps(request.get_json()), object_hook=lambda d: TrainRequest(**d))
    except ValueError:
        return {"msg": "Not all fields for the TrainRequest object were POSTed"}
    except TypeError:
        return {"msg": "Not all fields for the TrainRequest object were POSTed"}

    if requestData.shiftUUID is None or requestData.shiftUUID is "":
        return {'msg': "Your train request had no shiftUUID"}

    if requestData.usePTM is None:
        return {'msg': "Your train request had not indication to use the prebuilt model or not"}

    if requestData.epochs > 100:
        return {'msg': "Your train request will take too long"}

    if requestData.trainType != "basic" and requestData.trainType != "advanced":
        return {'msg': "Your train request did not have the correct training type"}

    if requestData.prebuiltShiftModel:
        try:
            tf.keras.models.load_model(os.path.join(current_app.config["SHIFT_MODELS_FOLDER"],
                                       requestData.prebuiltShiftModel, "encoder"))
            tf.keras.models.load_model(os.path.join(current_app.config["SHIFT_MODELS_FOLDER"],
                                       requestData.prebuiltShiftModel, "baseDecoder"))
        except OSError:
            return {'msg': "That model does not exist"}

    trainShift.delay(requestData)

    return {'msg': f"Training as {current_user.username}"}
