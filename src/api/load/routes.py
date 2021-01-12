#pylint: disable=C0103, C0301
"""
Routes for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
import json
from typing import List
from flask import Blueprint, request
from flask_login import login_required, current_user

#First Party Imports
from src.api.load import tasks
from src.utils.validators import (validateFilename,
                                  validateFileRequest)
from src.utils.files import generateUniqueFilename


load = Blueprint('load', __name__)


@load.route("/loadData", methods=["POST"])
@login_required
def loadData() -> dict:
    """
    Given training data Shift specializes a model for the training data. Yeilds
    more relaisitic results than just an inference though it takes longer.

    Request Header Arguments:
        trainingDataTypes: Whether the data is 'base' or 'mask'

    Request Body Arguments:
        file: The training data to be saved.

    Returns:
        Shifted Media: The media that has been shifted by the specialized model.
    """

    if not validateFileRequest(request.files):
        return {'msg': "The request payload had no file"}

    try:
        requestData: List[str] = json.loads(request.headers["trainingDataTypes"])
    except ValueError:
        return {"msg": "Not all fields for the LoadRequest object were POSTed"}
    except TypeError:
        return {"msg": "Not all fields for the TrainRequest object were POSTed"}

    if len(requestData) != len(request.files):
        return {'msg': "The number of training files and training data types does not match"}

    shiftUUID, _ = generateUniqueFilename()
    shiftUUID = str(shiftUUID)

    count = 0
    for _ in request.files:
        data = request.files[_]

        if data.filename == '':
            return {'msg': "The request had no selected file"}

        if data and validateFilename(data.filename):
            tasks.saveFlaskData.delay(requestData, data, shiftUUID, count)
        else:
            return {'msg': 'File not valid'}

        count += 1

    return {'msg': f"Loading data as {current_user.username}", "shiftUUID": shiftUUID}
