#pylint: disable=C0103, C0301
"""
Tasks for the inference endpoint of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
import os
import json
import numpy as np
from flask import current_app

#First Party Imports
from src.run import celery
from src.AI.shift import Shift
from src.utils.files import getMediaType
from src.DataModels.MongoDB.Shift import Shift as ShiftDataModel
from src.DataModels.Request.InferenceRequest import InferenceRequest
from src.utils.video import (loadVideo, extractAudio, insertAudio,
                             saveVideo)
from src.variables.constants import (HAAR_CASCADE_KWARGS, SHIFT_PATH,
                                     IMAGE_PATH, VIDEO_PATH)


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

    requestData: InferenceRequest = InferenceRequest(**requestJSON)

    shft = Shift(id_=requestData.shiftUUID)
    inferencingData = [np.ones(shft.imageShape)]
    shiftFilePath = os.path.join(current_app.root_path, SHIFT_PATH, shft.id_)

    if requestData.prebuiltShiftModel:
        shft.load(encoderPath=os.path.join(current_app.root_path, SHIFT_PATH,
                                           requestData.prebuiltShiftModel),
                  basePath=os.path.join(current_app.root_path, SHIFT_PATH,
                                        requestData.prebuiltShiftModel),
                  maskPath=shiftFilePath, readyToPredict=True, imageShape=shft.imageShape)

    else:
        shft.load(encoderPath=shiftFilePath, basePath=shiftFilePath,
                  maskPath=shiftFilePath, readyToPredict=True,
                  imageShape=shft.imageShape)

    mongoShift: ShiftDataModel = ShiftDataModel.objects.get(uuid=requestData.shiftUUID)
    baseMediaFilename = os.path.join(shiftFilePath, "tmp", "original", os.listdir(os.path.join(shiftFilePath, "tmp", "original"))[0])
    _, extension = os.path.splitext(baseMediaFilename)

    fps=30
    if getMediaType(baseMediaFilename) == 'video':
        fps = loadVideo(baseMediaFilename).fps

    inferencingData = list(shft.loadData(os.path.join(shiftFilePath, "tmp", "original"), 1, firstMedia=True))
    shifted = shft.shift(shft.maskAE, inferencingData, fps, **HAAR_CASCADE_KWARGS, gray=True)

    if getMediaType(baseMediaFilename) == 'video':
        baseAudio = extractAudio(loadVideo(baseMediaFilename))
        shifted = insertAudio(shifted, baseAudio)
        saveVideo(video=shifted, fps=fps, deleteOld=True,
                  path=os.path.join(current_app.root_path,
                                    VIDEO_PATH, f"{requestData.shiftUUID}{extension}"))
    elif getMediaType(baseMediaFilename) == 'image':
        shifted.save(os.path.join(current_app.root_path, IMAGE_PATH, f"{requestData.shiftUUID}{extension}"))
    
    mongoShift.update(set__mediaFilename=f"{requestData.shiftUUID}{extension}")

    del shft
