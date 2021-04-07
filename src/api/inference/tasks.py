#pylint: disable=C0103, C0301
"""
Tasks for the inference endpoint of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
import os
import cv2
import json
import random
import numpy as np
from flask import current_app

#First Party Imports
from src.run import celery
from src.AI.shift import Shift
from src.utils.files import getMediaType
from src.DataModels.MongoDB.User import User
from src.utils.image import encodeImage, saveImage
from src.variables.constants import HAAR_CASCADE_KWARGS
from src.DataModels.MongoDB.Shift import Shift as ShiftDataModel
from src.DataModels.JSON.InferenceRequest import InferenceRequest
from src.DataModels.MongoDB.InferenceWorker import InferenceWorker
from src.utils.video import (loadVideo, extractAudio, insertAudio,
                             saveVideo)


def loadPTM(requestData: InferenceRequest, shft: Shift):
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
                               requestData.prebuiltShiftModel, "baseDecoder"),
                  os.path.join(current_app.config["SHIFT_MODELS_FOLDER"], requestData.shiftUUID, "maskDecoder"))

    elif requestData.usePTM:
        shft.load(os.path.join(current_app.config["SHIFT_MODELS_FOLDER"],
                               "PTM", "encoder"),
                  os.path.join(current_app.config["SHIFT_MODELS_FOLDER"],
                               "PTM", "decoder"),
                  os.path.join(current_app.config["SHIFT_MODELS_FOLDER"],
                               "PTM", "decoder"))


@celery.task(name="inference.shift")
def shiftMedia(requestJSON: dict) -> str:
    """
    Shifts the media given the inference data and whether to load the
    PTM or a specialized model.

    Args:
        requestJSON (dict): The data that comes with the inference request in JSON form

    Returns:
        str: The encoded shift
    """

    requestData: InferenceRequest = json.loads(json.dumps(requestJSON), object_hook=lambda d: InferenceRequest(**d))
    worker: InferenceWorker = InferenceWorker.objects.get(shiftUUID=requestData.shiftUUID)

    shft = Shift(id_=requestData.shiftUUID)
    inferencingData = [np.ones(shft.imageShape)]
    shiftFilePath = os.path.join(current_app.config["SHIFT_MODELS_FOLDER"], shft.id_)

    if requestData.prebuiltShiftModel:
        shft.load(os.path.join(current_app.config["SHIFT_MODELS_FOLDER"],
                               requestData.prebuiltShiftModel, "encoder"),
                  os.path.join(current_app.config["SHIFT_MODELS_FOLDER"],
                               requestData.prebuiltShiftModel, "baseDecoder"),
                  os.path.join(shiftFilePath, "maskDecoder"))

    else:
        shft.load(os.path.join(shiftFilePath, "encoder"),
                  os.path.join(shiftFilePath, "baseDecoder"),
                  os.path.join(shiftFilePath, "maskDecoder"))

    baseVideoFilename = ""
    for name in os.listdir(os.path.join(shiftFilePath, "tmp")):
        if name.find("base") != -1:
            baseVideoFilename = os.path.join(shiftFilePath, "tmp", name)

    fps = loadVideo(baseVideoFilename).fps
    inferencingData = list(shft.loadData("base", os.path.join(shiftFilePath, "tmp"), 1, firstMedia=True))
    shifted = shft.shift(shft.maskAE, inferencingData, fps, **HAAR_CASCADE_KWARGS, gray=True)

    if getMediaType(baseVideoFilename) == 'video':
        baseAudio = extractAudio(loadVideo(baseVideoFilename))
        shifted = insertAudio(shifted, baseAudio)
        print(shifted.filename) ### Checking if deleteOld will work ###
        saveVideo(shifted, os.path.join(shiftFilePath, 'tmp', f"{requestData.shiftUUID}.mp4"), fps)
    elif getMediaType(baseVideoFilename) == 'image':
        shifted = cv2.cvtColor(shifted, cv2.COLOR_RGB2BGR)
        saveImage(shifted, os.path.join(shiftFilePath, 'tmp', f"{requestData.shiftUUID}.png"))


    del shft
