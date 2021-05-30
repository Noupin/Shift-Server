#pylint: disable=C0103, C0301
"""
Tasks for the training endpoint of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
import os
import numpy as np
from typing import List
from flask import current_app

#First Party Imports
from src.run import celery
from src.AI.shift import Shift
from src.DataModels.MongoDB.User import User
from src.DataModels.MongoDB.TrainWorker import TrainWorker
from src.DataModels.Request.TrainRequest import TrainRequest
from src.utils.memory import getAmountForBuffer, getGPUMemory
from src.DataModels.MongoDB.Shift import Shift as ShiftDataModel
from src.variables.constants import (OBJECT_CLASSIFIER, HAAR_CASCADE_KWARGS,
                                     LARGE_BATCH_SIZE, SHIFT_PATH)


def saveShiftToDatabase(uuid: str, author: User, title: str, path: str):
    """
    Saves the paths and the relevant information for a shift model to the database.

    Args:
        uuid (str): The unique identifier for the shift model
        author (User): The author of the shift
        title (str): The title of the shift model
        path (str): The path to the encoder, base decoder and mask decoder models
    """

    mongoShift = ShiftDataModel(uuid=uuid, author=author, title=title,
                                encoderPath=os.path.join(path, "encoder"),
                                baseDecoderPath=os.path.join(path, "baseDecoder"),
                                maskDecoderPath=os.path.join(path, "maskDecoder"))
    mongoShift.save()


def loadPTM(requestData: TrainRequest, shft: Shift):
    """
    Checks if a specialized mdoel was idnicated in the train request or loading the PTM if indicated.

    Args:
        requestData (TrainRequest): The data associated with the train request
        shft (Shift): The shft object to load the encoder, base and mask decoder
    """

    if requestData.prebuiltShiftModel:
        shft.load(os.path.join(current_app.root_path, SHIFT_PATH,
                               requestData.prebuiltShiftModel, "encoder"),
                  os.path.join(current_app.root_path, SHIFT_PATH,
                               requestData.prebuiltShiftModel, "baseDecoder"))

        if requestData.usePTM:
            shft.load(maskPath=os.path.join(current_app.root_path, SHIFT_PATH,
                                            "PTM", "maskDecoder"))

    elif requestData.usePTM:
        shft.load(os.path.join(current_app.root_path, SHIFT_PATH,
                               "PTM", "encoder"),
                  os.path.join(current_app.root_path, SHIFT_PATH,
                               "PTM", "decoder"),
                  os.path.join(current_app.root_path, SHIFT_PATH,
                               "PTM", "decoder"))


def getBasicExhibitImage(shft: Shift) -> List[np.ndarray]:
    """
    Uses the Shift object to get the data to return for the basic training view

    Args:
        shft (Shift): The shift models and variables

    Returns:
        list of str: An array with the encoded shifted image
    """

    inferencingData = shft.loadData(os.path.join(current_app.root_path, SHIFT_PATH, shft.id_, "tmp", "original"),
                                    1, action=OBJECT_CLASSIFIER, firstMedia=True, firstImage=True, **HAAR_CASCADE_KWARGS, gray=True)
    shiftedImage = shft.shift(shft.maskAE, next(inferencingData), **HAAR_CASCADE_KWARGS, gray=True)

    return [shiftedImage.encode()]


def getAdvancedExhibitImages(shft: Shift) -> List[np.ndarray]:
    """
    Uses the Shift object to get the data to return for the advanced training view

    Args:
        shft (Shift): The shift models and variables

    Returns:
        list of str: An array of the encoded shifted images
    """

    baseInferencingData = shft.loadData(os.path.join(current_app.root_path, SHIFT_PATH, shft.id_, "tmp", "original"),
                                        1, action=OBJECT_CLASSIFIER, firstMedia=True, firstImage=True, **HAAR_CASCADE_KWARGS, gray=True)
    maskInferencingData = shft.loadData(os.path.join(current_app.root_path, SHIFT_PATH, shft.id_, "tmp", "mask"),
                                        1, action=OBJECT_CLASSIFIER, firstMedia=True, firstImage=True, **HAAR_CASCADE_KWARGS, gray=True)

    baseImage = next(baseInferencingData)
    baseRemake = shft.shift(shft.baseAE, baseImage, **HAAR_CASCADE_KWARGS, gray=True)

    maskImage = next(maskInferencingData)
    maskRemake = shft.shift(shft.maskAE, maskImage, **HAAR_CASCADE_KWARGS, gray=True)

    shiftedImage = shft.shift(shft.maskAE, baseImage, **HAAR_CASCADE_KWARGS, gray=True)

    return [baseImage.encode(), baseRemake.encode(),
            maskImage.encode(), maskRemake.encode(), 
            shiftedImage.encode()]


@celery.task(name="train.trainShift")
def trainShift(requestJSON: dict, userID: str):
    """
    Trains the shift models from PTM or from a specialized model depending on the requestData.

    Args:
        requestJSON (dict): The JSON request data that can be serialized
        userID (str): The id of the user to query and save with the shift model
    """

    author = User.objects(id=userID).first()
    requestData: TrainRequest = TrainRequest(**requestJSON)
    worker: TrainWorker = TrainWorker.objects.get(shiftUUID=requestData.shiftUUID)

    shft = Shift(id_=requestData.shiftUUID)
    shiftFilePath = os.path.join(current_app.root_path, SHIFT_PATH, shft.id_)

    loadPTM(requestData, shft)

    if True: #Needs check for if the model is being retrained or iterativley trained Old Line: requestData.prebuiltShiftModel == ""
        originalImageList = shft.loadData(os.path.join(shiftFilePath, "tmp", "original"), action=OBJECT_CLASSIFIER, **HAAR_CASCADE_KWARGS, gray=True)
        baseImages = shft.loadData(os.path.join(shiftFilePath, "tmp", "base"), action=OBJECT_CLASSIFIER, **HAAR_CASCADE_KWARGS, gray=True)

        baseImageArray = list(shft.formatTrainingData(originalImageList, OBJECT_CLASSIFIER, **HAAR_CASCADE_KWARGS, gray=True))
        baseImageArray += list(shft.formatTrainingData(baseImages, OBJECT_CLASSIFIER, **HAAR_CASCADE_KWARGS, gray=True))

        baseTrainingData = np.array(baseImageArray)


        if requestData.prebuiltShiftModel:
            maskImages = shft.loadData(os.path.join(current_app.root_path, SHIFT_PATH, requestData.prebuiltShiftModel, "tmp", "mask"))
            maskTrainingData = np.array(list(shft.formatTrainingData(maskImages, OBJECT_CLASSIFIER, **HAAR_CASCADE_KWARGS, gray=True)))
        else:
            maskImages = shft.loadData(os.path.join(shiftFilePath, "tmp", "mask"), action=OBJECT_CLASSIFIER, **HAAR_CASCADE_KWARGS, gray=True)
            maskTrainingData = np.array(list(shft.formatTrainingData(maskImages, OBJECT_CLASSIFIER, **HAAR_CASCADE_KWARGS, gray=True)))


    ### Work Around ###
    try:
        shft.encoder.modelLoaded
        #Only needs built and compiled the first time
        shft.build()
        shft.compile()
    except AttributeError:
        pass

    #Subprocess cannot complete task "FileNotFoundError: [WinError 2] The system cannot find the file specified"
    amountForBuffer = LARGE_BATCH_SIZE#getAmountForBuffer(np.ones(shft.imageShape), sum(getGPUMemory()))

    training = worker.training
    while training:
        while not worker.inferencing and training:
            if not baseTrainingData is None and baseTrainingData.any():
                #print(f"\nTotal Base Training Images: {len(baseTrainingData.tolist())}\n")
                shft.baseAE.train(baseTrainingData, epochs=1, batch_size=(amountForBuffer, LARGE_BATCH_SIZE)[amountForBuffer > LARGE_BATCH_SIZE])
            if not maskTrainingData is None and maskTrainingData.any():
                #print(f"\nTotal Mask Training Images: {len(maskTrainingData.tolist())}\n")
                shft.maskAE.train(maskTrainingData, epochs=1, batch_size=(amountForBuffer, LARGE_BATCH_SIZE)[amountForBuffer > LARGE_BATCH_SIZE])
            
            worker.reload()
            training = worker.training

        if worker.inferencing:
            if requestData.trainType == "basic":
                worker.update(set__exhibitImages=getBasicExhibitImage(shft))
            elif requestData.trainType == "advanced":
                worker.update(set__exhibitImages=getAdvancedExhibitImages(shft))
                
            worker.update(set__inferencing=False, set__imagesUpdated=True)
            worker.reload()

    shft.save(shiftFilePath, shiftFilePath, shiftFilePath)

    saveShiftToDatabase(uuid=shft.id_, author=author, title=requestData.shiftTitle, path=shiftFilePath)

    del shft
