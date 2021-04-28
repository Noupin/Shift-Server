#pylint: disable=C0103, C0301
"""
Tasks for the inference endpoint of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
import os
import cv2
import json
import numpy as np
from flask import current_app

#First Party Imports
from src.run import celery
from src.AI.shift import Shift
from src.utils.files import getMediaType
from src.utils.image import saveImage
from src.DataModels.JSON.InferenceRequest import InferenceRequest
from src.DataModels.MongoDB.InferenceWorker import InferenceWorker
from src.DataModels.MongoDB.Shift import Shift as ShiftDataModel
from src.utils.video import (loadVideo, extractAudio, insertAudio,
                             saveVideo)
from src.variables.constants import (HAAR_CASCADE_KWARGS, SHIFT_PATH,
                                     IMAGE_PATH, VIDEO_PATH)


def loadPTM(requestData: InferenceRequest, shft: Shift):
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
                               requestData.prebuiltShiftModel, "baseDecoder"),
                  os.path.join(current_app.root_path, SHIFT_PATH,
                               requestData.shiftUUID, "maskDecoder"))

    elif requestData.usePTM:
        shft.load(os.path.join(current_app.root_path, SHIFT_PATH,
                               "PTM", "encoder"),
                  os.path.join(current_app.root_path, SHIFT_PATH,
                               "PTM", "decoder"),
                  os.path.join(current_app.root_path, SHIFT_PATH,
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
    shiftFilePath = os.path.join(current_app.root_path, SHIFT_PATH, shft.id_)

    if requestData.prebuiltShiftModel:
        shft.load(os.path.join(current_app.root_path, SHIFT_PATH,
                               requestData.prebuiltShiftModel, "encoder"),
                  os.path.join(current_app.root_path, SHIFT_PATH,
                               requestData.prebuiltShiftModel, "baseDecoder"),
                  os.path.join(shiftFilePath, "maskDecoder"))

    else:
        shft.load(os.path.join(shiftFilePath, "encoder"),
                  os.path.join(shiftFilePath, "baseDecoder"),
                  os.path.join(shiftFilePath, "maskDecoder"))

    mongoShift: ShiftDataModel = ShiftDataModel.objects.get(uuid=requestData.shiftUUID)
    baseMediaFilename = ""
    for name in os.listdir(os.path.join(shiftFilePath, "tmp", "original")):
        baseMediaFilename = os.path.join(shiftFilePath, "tmp", "original", name)

    fps = loadVideo(baseMediaFilename).fps
    inferencingData = list(shft.loadData(os.path.join(shiftFilePath, "tmp", "original"), 1, firstMedia=True))
    shifted = shft.shift(shft.maskAE, inferencingData, fps, **HAAR_CASCADE_KWARGS, gray=True)

    _, extension = os.path.splitext(baseMediaFilename)
    if getMediaType(baseMediaFilename) == 'video':
        baseAudio = extractAudio(loadVideo(baseMediaFilename))
        shifted = insertAudio(shifted, baseAudio)
        print(shifted.filename) ### Checking if deleteOld will work ###
        saveVideo(shifted, os.path.join(current_app.root_path, VIDEO_PATH, f"{requestData.shiftUUID}{extension}"), fps)
    elif getMediaType(baseMediaFilename) == 'image':
        shifted = cv2.cvtColor(shifted, cv2.COLOR_RGB2BGR)
        saveImage(shifted, os.path.join(current_app.root_path, IMAGE_PATH, f"{requestData.shiftUUID}{extension}"))
    
    mongoShift.update(set__imagePath=f"{requestData.shiftUUID}{extension}")

    del shft
