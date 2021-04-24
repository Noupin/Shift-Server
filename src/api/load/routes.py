#pylint: disable=C0103, C0301
"""
Routes for the Load part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
import os
import json
import werkzeug
from typing import List
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user
from flask import Blueprint, request, current_app, jsonify

#First Party Imports
from src.utils.files import makeDir
from src.utils.validators import (validateFilename,
                                  validateFileRequest)
from src.utils.files import generateUniqueFilename


loadBP = Blueprint('load', __name__)


def saveFlaskFile(data: werkzeug.datastructures.FileStorage, uuid: str, requestData: List[str], count=0):
    """
    Saves the data from a werkzeug file object to the file system

    Args:
        data (werkzeug.datastructures.FileStorage): The data to be saved to the file system.
        uuid (str): The uuid of the folder to save the files to.
        requestData (list of str): The additional data with the request needed for naming the file.
        count (int, optional): The counter to change the filename of the data
                               being saved. Defaults to 0.
    """

    filename = secure_filename(data.filename)
    _, extension = os.path.splitext(filename)

    folderPath = os.path.join(current_app.config["SHIFT_MODELS_FOLDER"], uuid)
    makeDir(folderPath)
    makeDir(os.path.join(folderPath, "tmp"))
    data.save(os.path.join(folderPath, "tmp",
                           "{}media{}{}".format(requestData[count], count+1, extension)))


@loadBP.route("/loadData", methods=["POST"])
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

    for count, _ in enumerate(request.files):
        data = request.files[_]

        if data.filename == '':
            return {'msg': "The request had no selected file"}

        if data and validateFilename(data.filename):
            saveFlaskFile(data, shiftUUID,requestData, count=count)
        else:
            return {'msg': 'File not valid'}

    return {'msg': f"Loaded data as {current_user.username}", "shiftUUID": shiftUUID}
