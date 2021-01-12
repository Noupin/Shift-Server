#pylint: disable=C0103, C0301
"""
Tasks for the training endpoint of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
import os
import numpy as np
from flask import current_app
from flask_login import current_user

#First Party Imports
from src.celery import celery
from src.AI.shift import Shift
from src.DataModels.MongoDB.User import User
from src.DataModels.JSON.TrainRequest import TrainRequest
from src.utils.memory import getAmountForBuffer, getGPUMemory
from src.DataModels.MongoDB.Shift import Shift as ShiftDataModel
from src.variables.constants import (OBJECT_CLASSIFIER, HAAR_CASCADE_KWARGS,
                                     LARGE_BATCH_SIZE)


def saveShiftToDatabase(uuid: str, userID, title: str, path: str):
    """
    Saves the paths and the relevant information for a shift model to the database.

    Args:
        uuid (str): The unique identifier for the shift model
        userID ([type]): The id of the user to associate the shift with
        title (str): The title of the shift model
        path (str): The path to the encoder, base decoder and mask decoder models
    """

    mongoShift = ShiftDataModel(uuid=uuid, userID=userID, title=title,
                                encoderFile=os.path.join(path, "encoder"),
                                baseDecoderFile=os.path.join(path, "baseDecoder"),
                                maskDecoderFile=os.path.join(path, "maskDecoder"))
    mongoShift.save()


def loadPTM(requestData: TrainRequest, shft: Shift):
    """
    Checks if a specialized mdoel was idnicated in the train request or loading the PTM if indicated.

    Args:
        requestData (TrainRequest): The data associated with the train request
        shft (Shift): The shft object to load the encoder, base and mask decoder
    """

    if requestData.prebuiltShiftModel:
        shft.load(os.path.join(current_app.config["SHIFT_MODELS_FOLDER"],
                               requestData.prebuiltShiftModel, "encoder"),
                  os.path.join(current_app.config["SHIFT_MODELS_FOLDER"],
                               requestData.prebuiltShiftModel, "baseDecoder"))

        if requestData.usePTM:
            shft.load(maskPath=os.path.join(current_app.config["SHIFT_MODELS_FOLDER"],
                                            "PTM", "maskDecoder"))

    elif requestData.usePTM:
        shft.load(os.path.join(current_app.config["SHIFT_MODELS_FOLDER"],
                               "PTM", "encoder"),
                  os.path.join(current_app.config["SHIFT_MODELS_FOLDER"],
                               "PTM", "decoder"),
                  os.path.join(current_app.config["SHIFT_MODELS_FOLDER"],
                               "PTM", "decoder"))


@celery.task(name="train.trainShift")
def trainShift(requestData: TrainRequest):
    """
    Trains the shift models from PTM or from a specialized model depending on the requestData.

    Args:
        requestData (TrainRequest): The data associated with the train request
    """

    shft = Shift(id_=requestData.shiftUUID)
    shiftFilePath = os.path.join(current_app.config["SHIFT_MODELS_FOLDER"], shft.id_)

    loadPTM(requestData, shft)

    if True: #Needs check for if the model is being retrained or iterativley trained Old Line: requestData.prebuiltShiftModel == ""
        baseImages = shft.loadData("base", os.path.join(shiftFilePath, "tmp"), action=OBJECT_CLASSIFIER, **HAAR_CASCADE_KWARGS, gray=True)
        baseTrainingData = shft.formatTrainingData(baseImages, OBJECT_CLASSIFIER, **HAAR_CASCADE_KWARGS, gray=True)

        if requestData.prebuiltShiftModel:
            maskImages = shft.loadData("mask", os.path.join(current_app.config["SHIFT_MODELS_FOLDER"], shft.id_, "tmp"))
            maskTrainingData = shft.formatTrainingData(maskImages, OBJECT_CLASSIFIER, **HAAR_CASCADE_KWARGS, gray=True)
        else:
            maskImages = shft.loadData("mask", os.path.join(shiftFilePath, "tmp"), action=OBJECT_CLASSIFIER, **HAAR_CASCADE_KWARGS, gray=True)
            maskTrainingData = shft.formatTrainingData(maskImages, OBJECT_CLASSIFIER, **HAAR_CASCADE_KWARGS, gray=True)

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
        #print(f"\nTotal Base Training Images: {len(baseTrainingData.tolist())}\n")
        shft.baseAE.train(baseTrainingData, epochs=requestData.epochs, batch_size=(amountForBuffer, LARGE_BATCH_SIZE)[amountForBuffer > LARGE_BATCH_SIZE])
    if not maskTrainingData is None and maskTrainingData.any():
        #print(f"\nTotal Mask Training Images: {len(maskTrainingData.tolist())}\n")
        shft.maskAE.train(maskTrainingData, epochs=requestData.epochs, batch_size=(amountForBuffer, LARGE_BATCH_SIZE)[amountForBuffer > LARGE_BATCH_SIZE])
    shft.save(shiftFilePath, shiftFilePath, shiftFilePath)

    saveShiftToDatabase(uuid=shft.id_, userID=current_user.id, title="Some title", path=shiftFilePath)

    del shft
