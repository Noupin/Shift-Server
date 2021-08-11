#pylint: disable=C0103, C0301
"""
Tasks for the training endpoint of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
import os
import numpy as np
import tensorflow as tf
from flask import current_app
from typing import List, Tuple

#First Party Imports
from src import db
from src.run import celery
from src.AI.Shift import Shift
from src.models.SQL.User import User
from TFMultiImage import TFMultiImage
from src.utils.dataset import datasetFrom
from src.utils.files import generateUniqueFilename
from src.models.SQL.TrainWorker import TrainWorker
from src.models.SQL.Shift import Shift as ShiftDataModel
from src.models.Request.TrainRequest import TrainRequest
from src.utils.memory import getAmountForBuffer, getGPUMemory
from src.constants import (EXHIBIT_IMAGE_COMPRESSION_QUALITY, IMAGE_PATH,
                                     OBJECT_DETECTOR, OBJECT_DETECTOR_KWARGS,
                                     LARGE_BATCH_SIZE, PTM_DECODER_REALTIVE_PATH,
                                     PTM_DISCRIMINATOR_REALTIVE_PATH,
                                     PTM_ENCODER_REALTIVE_PATH, SHIFT_PATH,
                                     LATENT_SPACE_DIM)


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
                                maskMediaFilename=maskImageFilename)
    db.session.add(mongoShift)
    db.session.commit()


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
                     baseDecoderPath=os.path.join(current_app.root_path, SHIFT_PATH,
                                                  requestData.prebuiltShiftModel))

        if requestData.usePTM:
            shiftAI.load(maskDecoderPath=os.path.join(current_app.root_path, SHIFT_PATH,
                                                      PTM_DECODER_REALTIVE_PATH),
                         maskDiscriminatorPath=os.path.join(current_app.root_path, SHIFT_PATH,
                                                            PTM_DISCRIMINATOR_REALTIVE_PATH),
                         absPath=True)

    elif requestData.usePTM:
        shiftAI.load(encoderPath=os.path.join(current_app.root_path, SHIFT_PATH,
                                              PTM_ENCODER_REALTIVE_PATH),
                     baseDecoderPath=os.path.join(current_app.root_path, SHIFT_PATH,
                                                  PTM_DECODER_REALTIVE_PATH),
                     baseDiscriminatorPath=os.path.join(current_app.root_path, SHIFT_PATH,
                                                        PTM_DISCRIMINATOR_REALTIVE_PATH),
                     maskDecoderPath=os.path.join(current_app.root_path, SHIFT_PATH,
                                                  PTM_DECODER_REALTIVE_PATH),
                     maskDiscriminatorPath=os.path.join(current_app.root_path, SHIFT_PATH,
                                                        PTM_DISCRIMINATOR_REALTIVE_PATH),
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
                                    1, action=OBJECT_DETECTOR, firstMedia=True, firstImage=True, **OBJECT_DETECTOR_KWARGS)
    shiftedImage = shft.shift(shft.maskAVA, next(inferencingData), **OBJECT_DETECTOR_KWARGS)
    shiftedImage.resize(maxDim=1000, keepAR=True)
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
                                        1, action=OBJECT_DETECTOR, firstMedia=True, firstImage=True, **OBJECT_DETECTOR_KWARGS)
    maskInferencingData = shft.loadData(os.path.join(current_app.root_path, SHIFT_PATH, shft.id_, "tmp", "mask"),
                                        1, action=OBJECT_DETECTOR, firstMedia=True, firstImage=True, **OBJECT_DETECTOR_KWARGS)

    exhibitArray: List[TFMultiImage] = []
    
    exhibitArray.append(next(baseInferencingData))
    exhibitArray.append(shft.shift(shft.baseAVA, exhibitArray[0].copy(), **OBJECT_DETECTOR_KWARGS))
    exhibitArray.append(next(maskInferencingData))
    exhibitArray.append(shft.shift(shft.maskAVA, exhibitArray[2].copy(), **OBJECT_DETECTOR_KWARGS))
    exhibitArray.append(shft.shift(shft.maskAVA, exhibitArray[0].copy(), **OBJECT_DETECTOR_KWARGS))

    for image in exhibitArray:
        image.resize(maxDim=500, keepAR=True)
        image.compress(quality=EXHIBIT_IMAGE_COMPRESSION_QUALITY)

    return [img.encode() for img in exhibitArray]


def saveBaseAndMaskImages(shft: Shift) -> Tuple[str, str]:
    """
    Uses the Shift object to save a base and mask image to the filesystem.

    Args:
        shft (Shift): The shift models and variables
    
    Returns:
        Tuple[str, str]: The base and mask filename.
    """

    _, basePreviewUUID = generateUniqueFilename()
    baseFilename = f"{basePreviewUUID}.png"
    baseImageGenerator = shft.loadData(os.path.join(current_app.root_path, SHIFT_PATH, shft.id_, "tmp", "original"),
                                       1, action=OBJECT_DETECTOR, firstMedia=True, firstImage=True, **OBJECT_DETECTOR_KWARGS)
    basePreviewImage = next(baseImageGenerator)
    basePreviewImage.resize(512, keepAR=True)
    basePreviewImage.save(os.path.join(current_app.root_path, IMAGE_PATH, baseFilename))

    _, maskPreviewUUID = generateUniqueFilename()
    maskFilename = f"{maskPreviewUUID}.png"
    maskImageGenerator = shft.loadData(os.path.join(current_app.root_path, SHIFT_PATH, shft.id_, "tmp", "mask"),
                                       1, action=OBJECT_DETECTOR, firstMedia=True, firstImage=True, **OBJECT_DETECTOR_KWARGS)
    maskPreviewImage = next(maskImageGenerator)
    maskPreviewImage.resize(512, keepAR=True)
    maskPreviewImage.save(os.path.join(current_app.root_path, IMAGE_PATH, maskFilename))
    
    return baseFilename, maskFilename


@celery.task(name="train.trainShift")
def trainShift(requestJSON: dict, userID: str):
    """
    Trains the shift models from PTM or from a specialized model depending on the requestData.

    Args:
        requestJSON (dict): The JSON request data that can be serialized
        userID (str): The id of the user to query and save with the shift model
    """

    author = User.query.filter_by(id=userID).first()
    requestData: TrainRequest = TrainRequest(**requestJSON)
    worker: TrainWorker = TrainWorker.query.filter_by.get(shiftUUID=requestData.shiftUUID)

    shiftFilePath = os.path.join(current_app.root_path, SHIFT_PATH, requestData.shiftUUID)

    shft = Shift(id_=requestData.shiftUUID, latentSpaceDimension=LATENT_SPACE_DIM)
    loadPTM(requestData, shft)
    
    #Subprocess cannot complete task "FileNotFoundError: [WinError 2] The system cannot find the file specified"
    amountForBuffer = LARGE_BATCH_SIZE#getAmountForBuffer(np.ones(shft.imageShape), sum(getGPUMemory()))
    batchSize=(amountForBuffer, LARGE_BATCH_SIZE)[amountForBuffer > LARGE_BATCH_SIZE]

    if True: #Needs check for if the model is being retrained or iterativley trained Old Line: requestData.prebuiltShiftModel == ""
        def baseGen():
            originalImageList = shft.loadData(os.path.join(shiftFilePath, "tmp", "original"), action=OBJECT_DETECTOR, **OBJECT_DETECTOR_KWARGS)
            baseImages = shft.loadData(os.path.join(shiftFilePath, "tmp", "base"), action=OBJECT_DETECTOR, **OBJECT_DETECTOR_KWARGS)

            for img in shft.formatTrainingData(originalImageList, OBJECT_DETECTOR, **OBJECT_DETECTOR_KWARGS):
                yield img
            
            for img in shft.formatTrainingData(baseImages, OBJECT_DETECTOR, **OBJECT_DETECTOR_KWARGS):
                yield img
        baseDataset = datasetFrom(baseGen, batchSize=batchSize,
                                  output_signature=(
                                    tf.TensorSpec(shape=shft.imageShape,
                                                        dtype=tf.float32)
                                  )
                                 )

        def maskGen():
            if requestData.prebuiltShiftModel:
                maskImages = shft.loadData(os.path.join(current_app.root_path, SHIFT_PATH, requestData.prebuiltShiftModel, "tmp", "mask"))
                for img in shft.formatTrainingData(maskImages, OBJECT_DETECTOR, **OBJECT_DETECTOR_KWARGS):
                    yield img
            else:
                maskImages = shft.loadData(os.path.join(shiftFilePath, "tmp", "mask"), action=OBJECT_DETECTOR, **OBJECT_DETECTOR_KWARGS)
                for img in shft.formatTrainingData(maskImages, OBJECT_DETECTOR, **OBJECT_DETECTOR_KWARGS):
                    yield img
        maskDataset = datasetFrom(maskGen, batchSize=batchSize,
                                  output_signature=(
                                    tf.TensorSpec(shape=shft.imageShape,
                                                        dtype=tf.float32)
                                  )
                                 )

    training = worker.training
    while training:
        while not worker.inferencing and training:
            if baseDataset:
                shft.baseAVA.train(baseDataset, epochs=1)
            if maskDataset:
                shft.maskAVA.train(maskDataset, epochs=1)
            
            training = worker.training

        if worker.inferencing:
            if requestData.trainType == "basic":
                worker.exhibitImages = getBasicExhibitImage(shft)
            elif requestData.trainType == "advanced":
                worker.exhibitImages = getAdvancedExhibitImages(shft)

            worker.inferencing = False
            worker.imagesUpdated = True
            db.session.commit()
            #Reload was taken out may need replacement

    shft.save(shiftFilePath, shiftFilePath, shiftFilePath)
    
    baseFilename, maskFilename = saveBaseAndMaskImages(shft)

    saveShiftToDatabase(uuid=shft.id_, author=author, title=requestData.shiftTitle, path=shiftFilePath,
                        baseImageFilename=baseFilename, maskImageFilename=maskFilename)

    del baseGen
    del maskGen
    del shft
