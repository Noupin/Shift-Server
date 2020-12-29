#pylint: disable=C0103, C0301
"""
Routes for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
import os
import flask
from flask import Blueprint, request, current_app
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user

#First Party Imports
from AI.shift import Shift
from src.constants import FILE_NAME_BYTE_SIZE
from src.utils.validators import validateFilename
from src.utils.files import generateUniqueFilename


api = Blueprint('api', __name__)


@api.route("/loadData", methods=["POST"])
@login_required
def loadData() -> dict:
    """
    Given training data Shift specializes a model for the training data. Yeilds
    more relaisitic results than just an inference though it takes longer. 

    Returns:
        Shifted Media: The media that has been shifted by the specialized model.
    """

    if 'file' not in request.files:
        return {'msg': "The request payload had no file"}

    data = request.files['file']
    if data.filename == '':
        return {'msg': "The request had no selected file"}
    
    if data and validateFilename(data.filename):
        filename = secure_filename(data.filename)
        _, extension = os.path.splitext(filename)
        uuid_ = generateUniqueFilename()

        data.save(os.path.join(current_app.config["USER_DATA_FOLDER"],
                               "videos",
                               f"{uuid_}{extension}"))
    else:
        return {'msg': 'File not valid'}
 
    return {'msg': f"Loaded data as {current_user}", "uuid": generateUniqueFilename()}


@api.route("/train", methods=["POST"])
@login_required
def train() -> dict:
    """
    Given training data Shift specializes a model for the training data. Yeilds
    more relaisitic results than just an inference though it takes longer. 

    Returns:
        Shifted Media: The media that has been shifted by the specialized model.
    """

    if not request.is_json:
        return {'msg': "Your train request had no JSON payload"}
    
    requestData = request.get_json()
    
    if not requestData["uuid"]:
        return {'msg': "Your train request had no uuid"}

    shft = Shift(id=requestData["uuid"])

    if requestData["shiftModel"]:
        try:
            shft.load(os.path.join(current_app.config["USER_DATA_FOLDER"],
                                   "shiftModels", "encoders", f"enc{requestData["uuid"]}"),
                      os.path.join(current_app.config["USER_DATA_FOLDER"],
                                   "shiftModels", "decoders", f"base{requestData["uuid"]}"))
        except OSError:
            return {'msg': "That model does not exist"}

 
    return {'msg': f"Training as {current_user}"}


@api.route("/inference", methods=["POST"])
@login_required
def inference() -> dict:
    """
    Inferenceing based on a specialized pretrained model(PTM) where, the input is
    the face to be put on the media and inferenced with PTM. Alternativley inferencing
    with a given base video and shift face with a non specialized PTM.

    Returns:
        Shifted Media: The media that has been shifted by the pretrained model.
    """

    return {'msg': f"Inferencing as {current_user}"}


@api.route('/featured', methods=["POST", "GET"])
def featured() -> dict:
    """
    Uses TCP to send the data of the two featured models.

    Returns:
        JSON: Contains the list of the featured models.
    """

    return {"data": ["Alpha + Beta\nBetter together", "Eta & Iota\nBetter Apart"]}


@api.route('/popular', methods=["POST", "GET"])
def popular() -> dict:
    """
    Uses TCP to send the data of the top 10 most popular models.

    Returns:
        JSON: Contains the list of the popular models.
    """

    return {"data": ["Black Panther", 
                     "Tony Stark",
                     "Captain America",
                     "Thor",
                     "Captain Marvel",
                     "Spider-Man",
                     "Robert Pattinson",
                     "Jesse Eisenberg",
                     "Andrew Garfield",
                     "Eleven"]}


@api.route('/new', methods=["POST", "GET"])
def new() -> dict:
    """
    Uses TCP to send the data of the 10 newest models.

    Returns:
        JSON: Contains the list of the new models.
    """

    return {"data": ["The Protagonist",
                     "Robert Pattinson",
                     "Timothy Chalamet",
                     "Tony Stark",
                     "Jimmy Falon",
                     "Black Panther",
                     "Andrew Garfield",
                     "Jesse Eisenberg",
                     "Black Panther",
                     "Chrisjen Ava Sarala"]}
