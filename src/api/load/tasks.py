#pylint: disable=C0103, C0301
"""
Routes for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
import os
import werkzeug
from typing import List
from flask import current_app
from werkzeug.utils import secure_filename

#First Party Imports
from src.celery import celery
from src.utils.files import makeDir


@celery.task(name="load.saveFlaskData")
def saveFlaskData(requestData: List[str], files: werkzeug.datastructures.MultiDict, shiftUUID: str, count: int) -> None:
    """
    Saves the files from the flask request to the correct place with
    the generatedUUID and a coutn to differentiate files.

    Args:
        requestData (list of str): The request data from the flask load request
        files (werkzeug.datastructures.MultiDict): The files sent with the request
        shiftUUID (str): The generated UUID to save the model to
        count (int): The count to differentiate the incoming data
    """

    filename = secure_filename(files.filename)
    _, extension = os.path.splitext(filename)

    folderPath = os.path.join(current_app.config["SHIFT_MODELS_FOLDER"], shiftUUID)
    makeDir(folderPath)
    makeDir(os.path.join(folderPath, "tmp"))
    files.save(os.path.join(folderPath, "tmp",
                            "{}media{}{}".format(requestData[count], count+1, extension)))
