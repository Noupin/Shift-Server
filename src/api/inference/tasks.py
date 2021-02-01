#pylint: disable=C0103, C0301
"""
Tasks for the inference endpoint of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
import os
import random
import numpy as np
from flask import current_app

#First Party Imports
from src.run import celery
from src.AI.shift import Shift
from src.utils.image import encodeImage
from src.DataModels.MongoDB.User import User
from src.DataModels.MongoDB.Shift import Shift as ShiftDataModel
from src.DataModels.JSON.InferenceRequest import InferenceRequest
from src.variables.constants import HAAR_CASCADE_KWARGS


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
def shift(requestData: InferenceRequest) -> str:
    """
    Shifts the object given the infernce data and whether to load the
    PTM or a specialized model.

    Args:
        requestData (InferenceRequest): The data that comes with the inference request

    Returns:
        str: The encoded shift
    """

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

    inferencingData = shft.loadData("base", os.path.join(shiftFilePath, "tmp"), 1, firstMedia=True)
    shiftedImage = shft.shift(shft.maskAE, random.choice(inferencingData), **HAAR_CASCADE_KWARGS, gray=True)
    encodedImage = encodeImage(shiftedImage)

    del shft
    return encodedImage
