#pylint: disable=C0103, C0301
"""
Routes for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
import os
import json
import flask
import random
import numpy as np
import tensorflow as tf
from typing import List
from flask import Blueprint, request, current_app
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user

#First Party Imports
from src.AI.shift import Shift
from src.utils.video import videoToImages
from src.utils.losses import bernoulliLoss
from src.DataModels.MongoDB.User import User
from src.utils.image import encodeImage, viewImage, decodeImage
from src.utils.validators import (validateFilename,
                                  validateFileRequest)
from src.DataModels.JSON.TrainRequest import TrainRequest
from src.utils.memory import getAmountForBuffer, getGPUMemory
from src.DataModels.MongoDB.Shift import Shift as ShiftDataModel
from src.DataModels.JSON.InferenceRequest import InferenceRequest
from src.variables.constants import (OBJECT_CLASSIFIER, HAAR_CASCADE_KWARGS,
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
            filename = secure_filename(data.filename)
            _, extension = os.path.splitext(filename)

            folderPath = os.path.join(current_app.config["SHIFT_MODELS_FOLDER"], shiftUUID)
            makeDir(folderPath)
            makeDir(os.path.join(folderPath, "tmp"))
            data.save(os.path.join(folderPath, "tmp",
                                   "{}media{}{}".format(requestData[count], count+1, extension)))
        else:
            return {'msg': 'File not valid'}
 
    return {'msg': f"Loaded data as {current_user}", "shiftUUID": shiftUUID}


@api.route("/train", methods=["POST"])
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
        return {'msg': "Your train request is too large and will exceed the TCP request timeout"}
    
    if requestData.trainType != "basic" and requestData.trainType != "advanced":
        return {'msg': "Your train request did not have the correct training type"}

    baseTrainingData = None
    maskTrainingData = None
    shft = Shift(id_=requestData.shiftUUID)
    shiftFilePath = os.path.join(current_app.config["SHIFT_MODELS_FOLDER"], shft.id_)

    if requestData.prebuiltShiftModel:
        try:
            shft.load(os.path.join(current_app.config["SHIFT_MODELS_FOLDER"],
                                   requestData.prebuiltShiftModel, "encoder"),
                      os.path.join(current_app.config["SHIFT_MODELS_FOLDER"],
                                   requestData.prebuiltShiftModel, "baseDecoder"),
                      os.path.join(current_app.config["SHIFT_MODELS_FOLDER"],
                                   requestData.prebuiltShiftModel, "maskDecoder"))
        except OSError:
            return {'msg': "That model does not exist"}

        if requestData.usePTM:
            shft.load(maskPath=os.path.join(current_app.config["SHIFT_MODELS_FOLDER"],
                                            "PTM", "maskDecoder"))
        maskImages = shft.loadData("mask", os.path.join(shiftFilePath, "tmp"))
        maskTrainingData = shft.formatTrainingData(maskImages, OBJECT_CLASSIFIER, **HAAR_CASCADE_KWARGS, gray=True)

    elif requestData.usePTM:
        shft.load(os.path.join(current_app.config["SHIFT_MODELS_FOLDER"],
                               "PTM", "encoder"),
                  os.path.join(current_app.config["SHIFT_MODELS_FOLDER"],
                               "PTM", "baseDecoder"),
                  os.path.join(current_app.config["SHIFT_MODELS_FOLDER"],
                               "PTM", "maskDecoder"))

    if True: #Needs check for if the model is being retrained or iterativley trained
        baseImages = shft.loadData("base", os.path.join(shiftFilePath, "tmp"), action=OBJECT_CLASSIFIER, **HAAR_CASCADE_KWARGS, gray=True)
        baseTrainingData = shft.formatTrainingData(baseImages, OBJECT_CLASSIFIER, **HAAR_CASCADE_KWARGS, gray=True)

        maskImages = shft.loadData("mask", os.path.join(shiftFilePath, "tmp"), action=OBJECT_CLASSIFIER, **HAAR_CASCADE_KWARGS, gray=True)
        maskTrainingData = shft.formatTrainingData(maskImages, OBJECT_CLASSIFIER, **HAAR_CASCADE_KWARGS, gray=True)

    if len(baseTrainingData) == 0 or len(maskTrainingData) == 0:
        return {'msg': "Your training data had no detectable faces."}
    
    ##
    #Work Around
    ##
    try:
        shft.encoder.modelLoaded
        #Only needs built and compiled the first time
        shft.build()
        shft.compile()
    except AttributeError:
        pass

    amountForBuffer = getAmountForBuffer(np.ones(shft.imageShape), sum(getGPUMemory()))

    if not baseTrainingData is None and baseTrainingData.any():
        print(f"\nTotal Base Training Images: {len(baseTrainingData.tolist())}\n")
        shft.baseAE.train(baseTrainingData, epochs=requestData.epochs, batch_size=(amountForBuffer, LARGE_BATCH_SIZE)[amountForBuffer > LARGE_BATCH_SIZE])
    if not maskTrainingData is None and maskTrainingData.any():
        print(f"\nTotal Mask Training Images: {len(maskTrainingData.tolist())}\n")
        shft.maskAE.train(maskTrainingData, epochs=requestData.epochs, batch_size=(amountForBuffer, LARGE_BATCH_SIZE)[amountForBuffer > LARGE_BATCH_SIZE])
    shft.save(shiftFilePath, shiftFilePath, shiftFilePath)


    #Updating MongoDB User with the new Shift
    mongoShift = ShiftDataModel(uuid=shft.id_, userID=current_user.id, title="Some title",
                                encoderFile=os.path.join(shiftFilePath, "encoder"),
                                baseDecoderFile=os.path.join(shiftFilePath, "baseDecoder"),
                                maskDecoderFile=os.path.join(shiftFilePath, "maskDecoder"))
    mongoShift.save()

    exhibitImages = []
    ##############################################################
    #Possible error when loading images not sure why need to test#
    ##############################################################
    if requestData.trainType == "basic":
        inferencingData = shft.loadData("base", os.path.join(shiftFilePath, "tmp"), 1, action=OBJECT_CLASSIFIER, firstMedia=True, firstImage=True, **HAAR_CASCADE_KWARGS, gray=True)

        shiftedImage = encodeImage(shft.shift(shft.maskAE, inferencingData[0], **HAAR_CASCADE_KWARGS, gray=True))
        exhibitImages.append(shiftedImage)
    elif requestData.trainType == "advanced":
        baseInferencingData = shft.loadData("base", os.path.join(shiftFilePath, "tmp"), 1, action=OBJECT_CLASSIFIER, firstMedia=True, firstImage=True, **HAAR_CASCADE_KWARGS, gray=True)
        maskInferencingData = shft.loadData("mask", os.path.join(shiftFilePath, "tmp"), 1, action=OBJECT_CLASSIFIER, firstMedia=True, firstImage=True, **HAAR_CASCADE_KWARGS, gray=True)

        baseImage = encodeImage(baseInferencingData[0])
        baseRemake = encodeImage(shft.shift(shft.baseAE, baseInferencingData[0], **HAAR_CASCADE_KWARGS, gray=True))

        maskImage = encodeImage(maskInferencingData[0])
        maskRemake = encodeImage(shft.shift(shft.maskAE, maskInferencingData[0], **HAAR_CASCADE_KWARGS, gray=True))

        shiftedImage = encodeImage(shft.shift(shft.maskAE, random.choice(inferencingData), **HAAR_CASCADE_KWARGS, gray=True))
        exhibitImages += [baseImage, baseRemake, maskImage, maskRemake, shiftedImage]

    del shft
    return {'msg': f"Trained as {current_user}", 'exhibit': exhibitImages}


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
    
    shft = Shift(id_=requestData.shiftUUID)
    inferencingData = [np.ones(shft.imageShape)]
    shiftFilePath = os.path.join(current_app.config["SHIFT_MODELS_FOLDER"], shft.id_)

    if requestData.prebuiltShiftModel:
        try:
            shft.load(os.path.join(current_app.config["SHIFT_MODELS_FOLDER"],
                                   requestData.prebuiltShiftModel, "encoder"),
                      os.path.join(current_app.config["SHIFT_MODELS_FOLDER"],
                                   requestData.prebuiltShiftModel, "baseDecoder"),
                      os.path.join(shiftFilePath, "maskDecoder"))
        except OSError:
            return {'msg': "That model does not exist"}

    else:
        shft.load(os.path.join(shiftFilePath, "encoder"),
                  os.path.join(shiftFilePath, "baseDecoder"),
                  os.path.join(shiftFilePath, "maskDecoder"))

    inferencingData = shft.loadData("base", os.path.join(shiftFilePath, "tmp"), 1, firstMedia=True)
    encodedImage = encodeImage(shft.shift(shft.maskAE, random.choice(inferencingData), **HAAR_CASCADE_KWARGS, gray=True))
    #viewImage(decodeImage(encodedImage))

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
