#pylint: disable=C0103, C0301
"""
Tasks for the inference endpoint of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
import gc
import os
import shutil
import numpy as np
from flask import current_app
from mutagen import File, FileType

#First Party Imports
from src import db
from src.run import celery
from src.AI.Shift import Shift
from src.models.SQL.Shift import Shift as ShiftDataModel
from src.models.SQL.InferenceWorker import InferenceWorker
from src.utils.files import generateUniqueFilename, getMediaType
from src.models.Request.InferenceRequest import InferenceRequest
from src.utils.video import (loadVideo, extractAudio, insertAudio,
                             saveVideo)
from src.constants import (OBJECT_DETECTOR_KWARGS, PTM_DECODER_REALTIVE_PATH,
                                     PTM_ENCODER_REALTIVE_PATH, SHIFT_IMAGE_METADATA_KEY,
                                     SHIFT_IMAGE_METADATA_VALUE, SHIFT_PATH, IMAGE_PATH,
                                     SHIFT_VIDEO_METADATA_KEY, SHIFT_VIDEO_METADATA_VALUE,
                                     VIDEO_PATH, DEFAULT_FPS, INFERENCE_IMAGE_PATH,
                                     LATENT_SPACE_DIM)


def loadModels(shiftInstance: Shift, requestData: InferenceRequest, shiftFilePath: str) -> Shift:
    if not requestData.training:
        shiftInstance.load(encoderPath=os.path.join(current_app.root_path, SHIFT_PATH,
                                                    PTM_ENCODER_REALTIVE_PATH),
                           baseDecoderPath=os.path.join(current_app.root_path, SHIFT_PATH,
                                                        PTM_DECODER_REALTIVE_PATH),
                           maskDecoderPath=os.path.join(current_app.root_path, SHIFT_PATH,
                                                        PTM_DECODER_REALTIVE_PATH),
                           absPath=True)

    elif requestData.prebuiltShiftModel:
        shiftInstance.load(encoderPath=os.path.join(current_app.root_path, SHIFT_PATH,
                                                    requestData.prebuiltShiftModel),
                           baseDecoderPath=os.path.join(current_app.root_path, SHIFT_PATH,
                                                        requestData.prebuiltShiftModel),
                           maskDecoderPath=shiftFilePath)

    else:
        shiftInstance.load(encoderPath=shiftFilePath,
                           baseDecoderPath=shiftFilePath,
                           maskDecoderPath=shiftFilePath)


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

    shft = Shift(id_=requestData.shiftUUID, latentSpaceDimension=LATENT_SPACE_DIM)
    inferencingData = [np.ones(shft.imageShape)]
    shiftFilePath = os.path.join(current_app.root_path, SHIFT_PATH, shft.id_)

    loadModels(shft, requestData, shiftFilePath)

    if requestData.training:
        try:
            mongoShift: ShiftDataModel = ShiftDataModel.query.filter_by(uuid=requestData.shiftUUID).first()
        except Exception:
            return "That shift model does not exist"
    else:
        worker: InferenceWorker = InferenceWorker.query.filter_by(shiftUUID=requestData.shiftUUID).first()

    baseMediaFilename = os.path.join(shiftFilePath, "tmp", "original", os.listdir(os.path.join(shiftFilePath, "tmp", "original"))[0])
    _, extension = os.path.splitext(baseMediaFilename)

    fps = DEFAULT_FPS
    if getMediaType(baseMediaFilename) == 'video':
        fps = loadVideo(baseMediaFilename).fps

    inferencingData = list(shft.loadData(os.path.join(shiftFilePath, "tmp", "original"), 1, firstMedia=True))
    shifted = shft.shift(shft.maskAVA, inferencingData, fps, **OBJECT_DETECTOR_KWARGS)

    if getMediaType(baseMediaFilename) == 'video':
        baseAudio = extractAudio(loadVideo(baseMediaFilename))
        shifted = insertAudio(shifted, baseAudio)
        saveVideo(video=shifted, fps=fps, deleteOld=True,
                  path=os.path.join(current_app.root_path,
                                    VIDEO_PATH, f"{requestData.shiftUUID}{extension}"))
        videoFolderPath = os.path.join(current_app.root_path, VIDEO_PATH) if requestData.training else os.path.join(current_app.root_path, INFERENCE_IMAGE_PATH)
        vid: FileType = File(videoFolderPath, f"{requestData.shiftUUID}{extension}")
        vid.tags[SHIFT_VIDEO_METADATA_KEY] = SHIFT_VIDEO_METADATA_VALUE
        vid.save()

    elif getMediaType(baseMediaFilename) == 'image':
        shifted.setMetadata(key=SHIFT_IMAGE_METADATA_KEY, value=SHIFT_IMAGE_METADATA_VALUE)
        if requestData.training:
            shifted.save(os.path.join(current_app.root_path, IMAGE_PATH, f"{requestData.shiftUUID}{extension}"))
        else:
            shifted.save(os.path.join(current_app.root_path, INFERENCE_IMAGE_PATH, f"{requestData.shiftUUID}{extension}"))

    if requestData.training:
        mongoShift.mediaFilename = f"{requestData.shiftUUID}{extension}"
        db.session.flush()
    else:
        try:
            shutil.rmtree(os.path.join(current_app.root_path, SHIFT_PATH, str(worker.shiftUUID)))
        except FileNotFoundError:
            pass

        baseMediaFilename = f"{generateUniqueFilename()[1]}{extension}"
        inferencingData[0].save(os.path.join(current_app.root_path, INFERENCE_IMAGE_PATH, baseMediaFilename))
        worker.mediaFilename = f"{requestData.shiftUUID}{extension}"
        worker.baseMediaFilename = baseMediaFilename
        db.session.flush()

    del shft
    gc.collect()
