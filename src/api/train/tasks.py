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
from src.utils.MultiImage import MultiImage
from src.utils.files import generateUniqueFilename

#First Party Imports
from src.run import celery
from src.AI.shift import Shift
from src.utils.image import viewImage
from src.DataModels.MongoDB.User import User
from src.DataModels.MongoDB.TrainWorker import TrainWorker
from src.DataModels.Request.TrainRequest import TrainRequest
from src.utils.memory import getAmountForBuffer, getGPUMemory
from src.DataModels.MongoDB.Shift import Shift as ShiftDataModel
from src.variables.constants import (EXHIBIT_IMAGE_COMPRESSION_QUALITY, IMAGE_PATH,
                                     OBJECT_CLASSIFIER, OBJECT_CLASSIFIER_KWARGS,
                                     LARGE_BATCH_SIZE, PTM_DECODER_REALTIVE_PATH,
                                     PTM_ENCODER_REALTIVE_PATH, SHIFT_PATH)


def saveShiftToDatabase(uuid: str, author: User, title: str, path: str,
                        baseImageFilename: str, maskImageFilename: str):
    """
    Saves the paths and the relevant information for a shift model to the database.

    Args:
        uuid (str): The unique identifier for the shift model
        author (User): The author of the shift
        title (str): The title of the shift model
        path (str): The path to the encoder, base decoder and mask decoder models
        baseImageFilename (str): The filename for the base preview image.
        maskImageFilename (str): The filename for the mask preview image.
    """

    mongoShift = ShiftDataModel(uuid=uuid, author=author, title=title,
                                baseMediaFilename=baseImageFilename,
                                maskMediaFilename=maskImageFilename,)
    mongoShift.save()


def loadPTM(requestData: TrainRequest, shiftAI: Shift):
    """
    Checks if a specialized mdoel was idnicated in the train request or loading the PTM if indicated.

    Args:
        requestData (TrainRequest): The data associated with the train request
        shft (Shift): The shft object to load the encoder, base and mask decoder
    """

    if requestData.prebuiltShiftModel:
        shiftAI.load(encoderPath=os.path.join(current_app.root_path, SHIFT_PATH,
                                              requestData.prebuiltShiftModel),
                     basePath=os.path.join(current_app.root_path, SHIFT_PATH,
                                           requestData.prebuiltShiftModel))

        if requestData.usePTM:
            shiftAI.load(maskPath=os.path.join(current_app.root_path, SHIFT_PATH,
                                               PTM_DECODER_REALTIVE_PATH), absPath=True)

    elif requestData.usePTM:
        shiftAI.load(encoderPath=os.path.join(current_app.root_path, SHIFT_PATH,
                                              PTM_ENCODER_REALTIVE_PATH),
                     basePath=os.path.join(current_app.root_path, SHIFT_PATH,
                                           PTM_DECODER_REALTIVE_PATH),
                     maskPath=os.path.join(current_app.root_path, SHIFT_PATH,
                                           PTM_DECODER_REALTIVE_PATH),
                     absPath=True)


def getBasicExhibitImage(shft: Shift) -> List[np.ndarray]:
    """
    Uses the Shift object to get the data to return for the basic training view

    Args:
        shft (Shift): The shift models and variables

    Returns:
        list of str: An array with the encoded shifted image
    """

    inferencingData = shft.loadData(os.path.join(current_app.root_path, SHIFT_PATH, shft.id_, "tmp", "original"),
                                    1, action=OBJECT_CLASSIFIER, firstMedia=True, firstImage=True, **OBJECT_CLASSIFIER_KWARGS)
    shiftedImage = shft.shift(shft.maskAE, next(inferencingData), **OBJECT_CLASSIFIER_KWARGS)
    shiftedImage.resize(width=1000, keepAR=True)
    shiftedImage.compress(quality=EXHIBIT_IMAGE_COMPRESSION_QUALITY)

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
                                        1, action=OBJECT_CLASSIFIER, firstMedia=True, firstImage=True, **OBJECT_CLASSIFIER_KWARGS)
    maskInferencingData = shft.loadData(os.path.join(current_app.root_path, SHIFT_PATH, shft.id_, "tmp", "mask"),
                                        1, action=OBJECT_CLASSIFIER, firstMedia=True, firstImage=True, **OBJECT_CLASSIFIER_KWARGS)

    exhibitArray: List[MultiImage] = []
    
    exhibitArray.append(next(baseInferencingData))
    exhibitArray.append(shft.shift(shft.baseAE, exhibitArray[0].copy(), **OBJECT_CLASSIFIER_KWARGS))
    exhibitArray.append(next(maskInferencingData))
    exhibitArray.append(shft.shift(shft.maskAE, exhibitArray[2].copy(), **OBJECT_CLASSIFIER_KWARGS))
    exhibitArray.append(shft.shift(shft.maskAE, exhibitArray[0].copy(), **OBJECT_CLASSIFIER_KWARGS))
    
    for image in exhibitArray:
        image.resize(width=500, keepAR=True)
        image.compress(quality=EXHIBIT_IMAGE_COMPRESSION_QUALITY)

    return [img.encode() for img in exhibitArray]


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

    shiftFilePath = os.path.join(current_app.root_path, SHIFT_PATH, requestData.shiftUUID)

    shft = Shift(id_=requestData.shiftUUID)
    loadPTM(requestData, shft)

    if True: #Needs check for if the model is being retrained or iterativley trained Old Line: requestData.prebuiltShiftModel == ""
        originalImageList = shft.loadData(os.path.join(shiftFilePath, "tmp", "original"), action=OBJECT_CLASSIFIER, **OBJECT_CLASSIFIER_KWARGS)
        baseImages = shft.loadData(os.path.join(shiftFilePath, "tmp", "base"), action=OBJECT_CLASSIFIER, **OBJECT_CLASSIFIER_KWARGS)

        baseImageArray = list(shft.formatTrainingData(originalImageList, OBJECT_CLASSIFIER, **OBJECT_CLASSIFIER_KWARGS))
        baseImageArray += list(shft.formatTrainingData(baseImages, OBJECT_CLASSIFIER, **OBJECT_CLASSIFIER_KWARGS))

        baseTrainingData = np.array(baseImageArray)


        if requestData.prebuiltShiftModel:
            maskImages = shft.loadData(os.path.join(current_app.root_path, SHIFT_PATH, requestData.prebuiltShiftModel, "tmp", "mask"))
            maskTrainingData = np.array(list(shft.formatTrainingData(maskImages, OBJECT_CLASSIFIER, **OBJECT_CLASSIFIER_KWARGS)))
        else:
            maskImages = shft.loadData(os.path.join(shiftFilePath, "tmp", "mask"), action=OBJECT_CLASSIFIER, **OBJECT_CLASSIFIER_KWARGS)
            maskTrainingData = np.array(list(shft.formatTrainingData(maskImages, OBJECT_CLASSIFIER, **OBJECT_CLASSIFIER_KWARGS)))

    shft.compile()

    #Subprocess cannot complete task "FileNotFoundError: [WinError 2] The system cannot find the file specified"
    amountForBuffer = LARGE_BATCH_SIZE#getAmountForBuffer(np.ones(shft.imageShape), sum(getGPUMemory()))

    training = worker.training
    while training:
        while not worker.inferencing and training:
            if not baseTrainingData is None and baseTrainingData.any():
                shft.baseAE.fit(x=baseTrainingData, y=baseTrainingData, epochs=1,
                                batch_size=(amountForBuffer, LARGE_BATCH_SIZE)[amountForBuffer > LARGE_BATCH_SIZE])
            if not maskTrainingData is None and maskTrainingData.any():
                shft.maskAE.fit(x=maskTrainingData, y=maskTrainingData, epochs=1,
                                batch_size=(amountForBuffer, LARGE_BATCH_SIZE)[amountForBuffer > LARGE_BATCH_SIZE])
            
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
    
    _, basePreviewUUID = generateUniqueFilename()
    baseFilename = f"{basePreviewUUID}.png"
    baseImageGenerator = shft.loadData(os.path.join(current_app.root_path, SHIFT_PATH, shft.id_, "tmp", "original"),
                                    1, action=OBJECT_CLASSIFIER, firstMedia=True, firstImage=True, **OBJECT_CLASSIFIER_KWARGS)
    basePreviewImage = next(baseImageGenerator)
    basePreviewImage.resize(512, keepAR=True)
    basePreviewImage.save(os.path.join(current_app.root_path, IMAGE_PATH, baseFilename))

    _, maskPreviewUUID = generateUniqueFilename()
    maskFilename = f"{maskPreviewUUID}.png"
    maskImageGenerator = shft.loadData(os.path.join(current_app.root_path, SHIFT_PATH, shft.id_, "tmp", "mask"),
                                    1, action=OBJECT_CLASSIFIER, firstMedia=True, firstImage=True, **OBJECT_CLASSIFIER_KWARGS)
    maskPreviewImage = next(maskImageGenerator)
    maskPreviewImage.resize(512, keepAR=True)
    maskPreviewImage.save(os.path.join(current_app.root_path, IMAGE_PATH, maskFilename))

    saveShiftToDatabase(uuid=shft.id_, author=author, title=requestData.shiftTitle, path=shiftFilePath,
                        baseImageFilename=baseFilename, maskImageFilename=maskFilename)

    del shft
