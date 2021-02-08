#pylint: disable=C0103, C0301
"""
The training route for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
import os
import json
import bson
import mongoengine
import tensorflow as tf
from celery.result import AsyncResult
from flask_login import login_required, current_user
from flask import Blueprint, request, current_app, session

#First Party Imports
from src.run import celery
from src.api.train.tasks import trainShift
from src.DataModels.MongoDB.User import User
from src.utils.MJSONEncoder import MongoJSONEncoder
from src.DataModels.JSON.TrainRequest import TrainRequest
from src.DataModels.MongoDB.TrainWorker import TrainWorker
from src.DataModels.MongoDB.Shift import Shift as ShiftDataModel


trainBP = Blueprint('train', __name__)


def validateBaseTrainRequest() -> TrainRequest or dict:
    if not request.is_json:
        return {'msg': "Your train request had no JSON payload"}

    try:
        requestData: TrainRequest = json.loads(json.dumps(request.get_json()), object_hook=lambda d: TrainRequest(**d))
    except ValueError as e:
        print("Value:", e)
        return {"msg": "Not all fields for the TrainRequest object were POSTed"}
    except TypeError as e:
        print("Type:", e)
        return {"msg": "Not all fields for the TrainRequest object were POSTed"}

    if requestData.shiftUUID is None or requestData.shiftUUID is "":
        return {'msg': "Your train request had no shiftUUID"}

    if requestData.usePTM is None:
        return {'msg': "Your train request had not indication to use the prebuilt model or not"}

    if requestData.trainType != "basic" and requestData.trainType != "advanced":
        return {'msg': "Your train request did not have the correct training type"}
    
    return requestData


@trainBP.route("/train", methods=["POST"])
@login_required
def train() -> dict:
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

    requestData = validateBaseTrainRequest()
    if type(requestData) == dict:
        return requestData

    if requestData.prebuiltShiftModel:
        try:
            tf.keras.models.load_model(os.path.join(current_app.config["SHIFT_MODELS_FOLDER"],
                                       requestData.prebuiltShiftModel, "encoder"))
            tf.keras.models.load_model(os.path.join(current_app.config["SHIFT_MODELS_FOLDER"],
                                       requestData.prebuiltShiftModel, "baseDecoder"))
        except OSError:
            return {'msg': "That model does not exist"}

    worker = TrainWorker(shiftUUID=requestData.shiftUUID, training=True, inferencing=False)
    job = trainShift.delay(request.get_json(), str(current_user.id))
    worker.workerID = job.id

    try:
        worker.save()
    except mongoengine.errors.NotUniqueError:
        return {'msg': "That AI is already training."}

    return {'msg': f"Training as {current_user.username}"}


@trainBP.route("/trainStatus", methods=["POST"])
@login_required
def trainStatus() -> dict:
    """
    The status of of the current training task if called while training the task
    will switch to give an update image. After a certain amount of time the training
    will be completed automatically to allow for multiple users to train.

    Returns:
        dict: A response with the status of the training and possibly exhibit images if ready.
    """

    requestData = validateBaseTrainRequest()
    if type(requestData) == dict:
        return requestData

    worker: TrainWorker = TrainWorker.objects.get(shiftUUID=requestData.shiftUUID)
    job = AsyncResult(id=worker.workerID, backend=celery._get_backend())

    try:
        status = job.status

        if status == "PENDING":
            worker.update(set__inferencing=True)
            worker.reload()

            imagesUpdated = worker.imagesUpdated
            while not imagesUpdated:
                worker.reload()
                imagesUpdated = worker.imagesUpdated

            if len(worker.exhibitImages) > 0 and worker.imagesUpdated:
                worker.update(set__imagesUpdated=False)
                worker.reload()

                return {'msg': f"Update for current shift", 'exhibit': worker.exhibitImages}

        return {'msg': f"The status is {status}"}

    except AttributeError as e:
        return {'msg': "There are currently no jobs"}


@trainBP.route("/stopTraining", methods=["POST"])
@login_required
def stopTrain() -> dict:
    """
    Stop the training with the UUID of the shift model being trained.

    Returns:
        dict: A msg confirming the cancellation of the shift training.
    """

    requestData = validateBaseTrainRequest()
    if type(requestData) == dict:
        return requestData

    worker: TrainWorker = TrainWorker.objects.get(shiftUUID=requestData.shiftUUID)
    worker.update(set__training=False)

    while True:
        try:
            worker.reload()
        except mongoengine.errors.DoesNotExist:
            break

    return {'msg': "Training stopped", 'stopped': True}
