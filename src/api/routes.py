#pylint: disable=C0103, C0301
"""
Routes for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
import os
import flask
import numpy as np
from flask import Blueprint, request, current_app
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user

#First Party Imports
from src.AI.shift import Shift
from src.DataModels.User import User
from src.utils.video import videoToImages
from src.utils.validators import validateFilename
from src.utils.image import encodeImage, viewImage
from src.DataModels.Shift import Shift as ShiftDataModel
from src.utils.memory import getAmountForBuffer, getGPUMemory
from src.constants import (FILE_NAME_BYTE_SIZE, OBJECT_CLASSIFIER,
                           LARGE_BATCH_SIZE)
from src.utils.files import (generateUniqueFilename, checkPathExists,
                             makeDir, getMediaType)


api = Blueprint('api', __name__)


@api.route("/loadData", methods=["POST"])
@login_required
def loadData() -> dict:
    """
    Given training data Shift specializes a model for the training data. Yeilds
    more relaisitic results than just an inference though it takes longer. 

    Request Header Arguments:
        dataType: Whether the data is 'base' or 'mask'
    
    Request Body Arguments:
        file: The training data to be saved.

    Returns:
        Shifted Media: The media that has been shifted by the specialized model.
    """

    if 'file' not in request.files:
        return {'msg': "The request payload had no file"}
    
    if request.headers["dataType"]  == None:
        return {'msg': "The request had no dataType item in the header"}
    
    if request.headers["dataType"] != "mask" and request.headers["dataType"] != "base":
        return {'msg': "The dataType is incorrect"}

    data = request.files['file']

    if data.filename == '':
        return {'msg': "The request had no selected file"}
    
    if data and validateFilename(data.filename):
        filename = secure_filename(data.filename)
        _, extension = os.path.splitext(filename)
        uuid_, _ = generateUniqueFilename()
        uuid_ = str(uuid_)

        folderPath = os.path.join(current_app.config["SHIFT_MODELS_FOLDER"], uuid_)
        makeDir(folderPath)
        makeDir(os.path.join(folderPath, "tmp"))
        data.save(os.path.join(folderPath, "tmp",
                               "{}media{}".format(request.headers["dataType"], extension)))
    else:
        return {'msg': 'File not valid'}
 
    return {'msg': f"Loaded data as {current_user}", "uuid": uuid_}


@api.route("/train", methods=["POST"])
@login_required
def train() -> dict:
    """
    Given training data Shift specializes a model for the training data. Yeilds
    more relaisitic results than just an inference though it takes longer. 

    Request Body Arguments:
        uuid (str): The UUID of the current training situation
        usePTM (bool): Whether or not to use the pre-trained model to enhace shifting
        prebuiltShiftModel (str): The id of the prebuilt model to use or an empty
                                  string if not using a prebuilt model

    Returns:
        Shifted Media: The media that has been shifted by the specialized model.
    """

    if not request.is_json:
        return {'msg': "Your train request had no JSON payload"}
    
    requestData = request.get_json()
    
    if requestData["uuid"] is None or requestData["uuid"] is "":
        return {'msg': "Your train request had no uuid"}
    

    
    if requestData["usePTM"] is None:
        return {'msg': "Your train request had not indication to use the prebuilt model or not"}

    baseTrainingData = None
    maskTrainingData = None
    shft = Shift(id_=requestData["uuid"])
    shiftFilePath = os.path.join(current_app.config["SHIFT_MODELS_FOLDER"], shft.id_)

    if requestData["prebuiltShiftModel"]:
        try:
            shft.load(os.path.join(current_app.config["SHIFT_MODELS_FOLDER"],
                                   requestData["prebuiltShiftModel"], "encoder"),
                      os.path.join(current_app.config["SHIFT_MODELS_FOLDER"],
                                   requestData["prebuiltShiftModel"], "baseDecoder"))
        except OSError:
            return {'msg': "That model does not exist"}

        if requestData["usePTM"]:
            shft.load(maskPath=os.path.join(current_app.config["SHIFT_MODELS_FOLDER"],
                                            "PTM", "maskDecoder"))
        maskImages = shft.loadData("mask", os.path.join(shiftFilePath, "tmp"))
        maskTrainingData = shft.formatTrainingData(maskImages, OBJECT_CLASSIFIER, scaleFactor=1.15, minNeighbors=4, minSize=(30, 30), gray=True)

    elif requestData["usePTM"]:
        shft.load(os.path.join(current_app.config["SHIFT_MODELS_FOLDER"],
                               "PTM", "encoder"),
                  os.path.join(current_app.config["SHIFT_MODELS_FOLDER"],
                               "PTM", "baseDecoder"),
                  os.path.join(current_app.config["SHIFT_MODELS_FOLDER"],
                               "PTM", "maskDecoder"))

    if requestData["prebuiltShiftModel"] == "":
        baseImages = shft.loadData("base", os.path.join(shiftFilePath, "tmp"))
        baseTrainingData = shft.formatTrainingData(baseImages, OBJECT_CLASSIFIER, scaleFactor=1.15, minNeighbors=4, minSize=(30, 30), gray=True)

        maskImages = shft.loadData("mask", os.path.join(shiftFilePath, "tmp"))
        maskTrainingData = shft.formatTrainingData(maskImages, OBJECT_CLASSIFIER, scaleFactor=1.15, minNeighbors=4, minSize=(30, 30), gray=True)
    
    shft.build()
    shft.compile()

    amountForBuffer = getAmountForBuffer(np.ones(shft.imageShape), sum(getGPUMemory()))
    print("VRAM Amount:", (amountForBuffer, LARGE_BATCH_SIZE)[amountForBuffer > LARGE_BATCH_SIZE])
    if not maskTrainingData is None and maskTrainingData.any():
        shft.maskAE.fit(maskTrainingData, maskTrainingData, epochs=10,
                        batch_size=(amountForBuffer, LARGE_BATCH_SIZE)[amountForBuffer > LARGE_BATCH_SIZE])
        shft.maskAE.summary()
    if not baseTrainingData is None and baseTrainingData.any():
        shft.baseAE.fit(baseTrainingData, baseTrainingData, epochs=10,
                        batch_size=(amountForBuffer, LARGE_BATCH_SIZE)[amountForBuffer > LARGE_BATCH_SIZE])
        shft.baseAE.summary()
    shft.save(shiftFilePath, shiftFilePath, shiftFilePath)


    shiftDataModel = ShiftDataModel(uuid=shft.id_, title="Some title",
                                    encoderFile=os.path.join(shiftFilePath, "encoder"),
                                    baseDecoderFile=os.path.join(shiftFilePath, "baseDecoder"),
                                    maskDecoderFile=os.path.join(shiftFilePath, "maskDecoder"))
    updated = User.objects(shifts__uuid=shiftDataModel.uuid).update_one(set__shifts__S=shiftDataModel)
    if not updated:
        User.objects.update_one(push__shifts=shiftDataModel)

    del shft
    return {'msg': f"Trained as {current_user}"}


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

    if not request.is_json:
        return {'msg': "Your inference request had no JSON payload"}
    
    requestData = request.get_json()
    
    if requestData["uuid"] is None or requestData["uuid"] is "":
        return {'msg': "Your inference request had no uuid"}
    
    if requestData["usePTM"] is None:
        return {'msg': "Your inference request had not indication to use the prebuilt model or not"}
    
    shft = Shift(id_=requestData["uuid"])
    inferencingData = [np.ones(shft.imageShape)]
    shiftFilePath = os.path.join(current_app.config["SHIFT_MODELS_FOLDER"], shft.id_)

    if requestData["prebuiltShiftModel"]:
        try:
            shft.load(os.path.join(current_app.config["SHIFT_MODELS_FOLDER"],
                                   requestData["prebuiltShiftModel"], "encoder"),
                      os.path.join(current_app.config["SHIFT_MODELS_FOLDER"],
                                   requestData["prebuiltShiftModel"], "baseDecoder"),
                      os.path.join(shiftFilePath, "maskDecoder"))
        except OSError:
            return {'msg': "That model does not exist"}

    else:
        shft.load(os.path.join(shiftFilePath, "encoder"),
                  os.path.join(shiftFilePath, "baseDecoder"),
                  os.path.join(shiftFilePath, "maskDecoder"))

    inferencingData = shft.loadData("base", os.path.join(shiftFilePath, "tmp"))
    encodedImage = encodeImage(shft.shift(shft.maskAE, inferencingData[0], scaleFactor=1.15, minNeighbors=4, minSize=(30, 30), gray=True))

    del shft
    return {'msg': f"Inferenced as {current_user}", "testImage": encodedImage}


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
