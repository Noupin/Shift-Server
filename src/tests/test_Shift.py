#pylint: disable=C0103, C0301
"""
Testing Suite for Shift class.
"""
__author__ = "Noupin"

#Third Party Imports
import numpy as np
from typing import List
import moviepy.editor as mediaEditor

#First Party Imports
from src.AI.Shift import Shift
from TFMultiImage import TFMultiImage
from src.utils.detection import detectObject
from src.utils.math import getLargestRectangle
from src.utils.video import loadVideo, videoToImages
from src.constants import OBJECT_DETECTOR_KWARGS, OBJECT_DETECTOR, SHIFT_STATIC_PATH, FERYV_STATIC_PATH


def test_EmptyConstructor():
    shft = Shift()

    assert isinstance(shft, Shift)


def test_EmptyConstructorZeroLayers():
    shft = Shift(codingLayers=0)

    assert isinstance(shft, Shift)
    

def test_EmptyConstructorOneLayers():
    shft = Shift(codingLayers=1)

    assert isinstance(shft, Shift)


def test_FormatTrainingData():
    baseMedia: List[TFMultiImage] = []
    maskMedia: List[TFMultiImage] = []

    for image in videoToImages(f"{FERYV_STATIC_PATH}\video\default.mp4",
                            action=OBJECT_DETECTOR, **OBJECT_DETECTOR_KWARGS, interval=100):
        baseMedia.append(TFMultiImage(image))
    for image in videoToImages(f"{FERYV_STATIC_PATH}\video\default.mp4",
                            action=OBJECT_DETECTOR, **OBJECT_DETECTOR_KWARGS, interval=100):
        maskMedia.append(TFMultiImage(image))

    shft = Shift()

    baseTrainingData = list(shft.formatTrainingData(baseMedia, **OBJECT_DETECTOR_KWARGS))
    maskTrainingData = list(shft.formatTrainingData(maskMedia, **OBJECT_DETECTOR_KWARGS))
    
    assert baseTrainingData[0].shape == shft.imageShape
    assert maskTrainingData[0].shape == shft.imageShape


def test_LoadModel():
    shft = Shift()

    shft.load(encoderPath=f"{SHIFT_STATIC_PATH}\shift\PTM\Encoder\Encoder",
              basePath=f"{SHIFT_STATIC_PATH}\shift\PTM\Decoder\Decoder",
              maskPath=f"{SHIFT_STATIC_PATH}\shift\PTM\Decoder\Decoder")


def test_Compile():
    shft = Shift()
    shft.compile()
    
    assert isinstance(shft, Shift)


def test_TFTraining():
    baseMedia: List[TFMultiImage] = []
    maskMedia: List[TFMultiImage] = []

    for image in videoToImages(f"{FERYV_STATIC_PATH}\video\default.mp4",
                            action=OBJECT_DETECTOR, **OBJECT_DETECTOR_KWARGS, interval=100):
        baseMedia.append(TFMultiImage(image))
    for image in videoToImages(f"{FERYV_STATIC_PATH}\video\default.mp4",
                            action=OBJECT_DETECTOR, **OBJECT_DETECTOR_KWARGS, interval=100):
        maskMedia.append(TFMultiImage(image))

    shft = Shift()

    baseTrainingData = np.array(list(shft.formatTrainingData(baseMedia, **OBJECT_DETECTOR_KWARGS)))
    maskTrainingData = np.array(list(shft.formatTrainingData(maskMedia, **OBJECT_DETECTOR_KWARGS)))
    
    shft.compile()
    
    shft.baseAE.fit(baseTrainingData, baseTrainingData, batch_size=16, epochs=1)
    shft.maskAE.fit(maskTrainingData, maskTrainingData, batch_size=16, epochs=1)


def test_TFTrainingLoadedModel():
    baseMedia: List[TFMultiImage] = []
    maskMedia: List[TFMultiImage] = []

    for image in videoToImages(f"{FERYV_STATIC_PATH}\video\default.mp4",
                            action=OBJECT_DETECTOR, **OBJECT_DETECTOR_KWARGS, interval=100):
        baseMedia.append(TFMultiImage(image))
    for image in videoToImages(f"{FERYV_STATIC_PATH}\video\default.mp4",
                            action=OBJECT_DETECTOR, **OBJECT_DETECTOR_KWARGS, interval=100):
        maskMedia.append(TFMultiImage(image))

    shft = Shift()
    
    shft.load(encoderPath=f"{SHIFT_STATIC_PATH}\shift\PTM\Encoder\Encoder",
              basePath=f"{SHIFT_STATIC_PATH}\shift\PTM\Decoder\Decoder",
              maskPath=f"{SHIFT_STATIC_PATH}\shift\PTM\Decoder\Decoder")

    baseTrainingData = np.array(list(shft.formatTrainingData(baseMedia, **OBJECT_DETECTOR_KWARGS)))
    maskTrainingData = np.array(list(shft.formatTrainingData(maskMedia, **OBJECT_DETECTOR_KWARGS)))
    
    shft.compile()
    
    shft.baseAE.fit(baseTrainingData, baseTrainingData, batch_size=16, epochs=1)
    shft.maskAE.fit(maskTrainingData, maskTrainingData, batch_size=16, epochs=1)


def test_PredictUntrainedModel():
    shft = Shift()

    images = videoToImages(f"{FERYV_STATIC_PATH}\video\default.mp4",
                          action=OBJECT_DETECTOR, **OBJECT_DETECTOR_KWARGS, interval=100)
    image = TFMultiImage(next(images))
    objects = detectObject(OBJECT_DETECTOR, image=image.CVImage, **OBJECT_DETECTOR_KWARGS)
    image.crop(getLargestRectangle(objects))
    image.resize(width=shft.imageShape[0], height=shft.imageShape[1])
    
    predicted = shft.inference(shft.baseAE, image.TFImage)
    
    assert predicted.CVImage.shape == shft.imageShape


def test_PredictTFTrainedModel():
    baseMedia: List[TFMultiImage] = []
    maskMedia: List[TFMultiImage] = []

    for image in videoToImages(f"{FERYV_STATIC_PATH}\video\default.mp4",
                            action=OBJECT_DETECTOR, **OBJECT_DETECTOR_KWARGS, interval=100):
        baseMedia.append(TFMultiImage(image))
    for image in videoToImages(f"{FERYV_STATIC_PATH}\video\default.mp4",
                            action=OBJECT_DETECTOR, **OBJECT_DETECTOR_KWARGS, interval=100):
        maskMedia.append(TFMultiImage(image))

    shft = Shift()

    baseTrainingData = np.array(list(shft.formatTrainingData(baseMedia, **OBJECT_DETECTOR_KWARGS)))
    maskTrainingData = np.array(list(shft.formatTrainingData(maskMedia, **OBJECT_DETECTOR_KWARGS)))
    
    shft.compile()
    
    shft.baseAE.fit(baseTrainingData, baseTrainingData, batch_size=16, epochs=1)
    shft.maskAE.fit(maskTrainingData, maskTrainingData, batch_size=16, epochs=1)

    images = videoToImages(f"{FERYV_STATIC_PATH}\video\default.mp4",
                          action=OBJECT_DETECTOR, **OBJECT_DETECTOR_KWARGS, interval=100)
    image = TFMultiImage(next(images))
    objects = detectObject(OBJECT_DETECTOR, image=image.CVImage, **OBJECT_DETECTOR_KWARGS)
    image.crop(getLargestRectangle(objects))
    image.resize(width=shft.imageShape[0], height=shft.imageShape[1])
    
    predicted = shft.inference(shft.baseAE, image.TFImage)
    
    assert predicted.CVImage.shape == shft.imageShape


def test_PredictLoadedModel():
    shft = Shift()

    shft.load(encoderPath=f"{SHIFT_STATIC_PATH}\shift\PTM\Encoder\Encoder",
              basePath=f"{SHIFT_STATIC_PATH}\shift\PTM\Decoder\Decoder",
              maskPath=f"{SHIFT_STATIC_PATH}\shift\PTM\Decoder\Decoder")

    images = videoToImages(f"{FERYV_STATIC_PATH}\video\default.mp4",
                          action=OBJECT_DETECTOR, **OBJECT_DETECTOR_KWARGS, interval=100)
    image = TFMultiImage(next(images))
    objects = detectObject(OBJECT_DETECTOR, image=image.CVImage, **OBJECT_DETECTOR_KWARGS)
    image.crop(getLargestRectangle(objects))
    image.resize(width=shft.imageShape[0], height=shft.imageShape[1])
    
    predicted = shft.inference(shft.baseAE, image.TFImage)
    
    assert predicted.CVImage.shape == shft.imageShape


def test_PredictTFTrainedLoadedModel():
    baseMedia: List[TFMultiImage] = []
    maskMedia: List[TFMultiImage] = []

    for image in videoToImages(f"{FERYV_STATIC_PATH}\video\default.mp4",
                            action=OBJECT_DETECTOR, **OBJECT_DETECTOR_KWARGS, interval=100):
        baseMedia.append(TFMultiImage(image))
    for image in videoToImages(f"{FERYV_STATIC_PATH}\video\default.mp4",
                            action=OBJECT_DETECTOR, **OBJECT_DETECTOR_KWARGS, interval=100):
        maskMedia.append(TFMultiImage(image))

    shft = Shift()
    
    shft.load(encoderPath=f"{SHIFT_STATIC_PATH}\shift\PTM\Encoder\Encoder",
              basePath=f"{SHIFT_STATIC_PATH}\shift\PTM\Decoder\Decoder",
              maskPath=f"{SHIFT_STATIC_PATH}\shift\PTM\Decoder\Decoder")

    baseTrainingData = np.array(list(shft.formatTrainingData(baseMedia, **OBJECT_DETECTOR_KWARGS)))
    maskTrainingData = np.array(list(shft.formatTrainingData(maskMedia, **OBJECT_DETECTOR_KWARGS)))
    
    shft.compile()
    
    shft.baseAE.fit(baseTrainingData, baseTrainingData, batch_size=16, epochs=1)
    shft.maskAE.fit(maskTrainingData, maskTrainingData, batch_size=16, epochs=1)

    images = videoToImages(f"{FERYV_STATIC_PATH}\video\default.mp4",
                          action=OBJECT_DETECTOR, **OBJECT_DETECTOR_KWARGS, interval=100)
    image = TFMultiImage(next(images))
    objects = detectObject(OBJECT_DETECTOR, image=image.CVImage, **OBJECT_DETECTOR_KWARGS)
    image.crop(getLargestRectangle(objects))
    image.resize(width=shft.imageShape[0], height=shft.imageShape[1])
    
    predicted = shft.inference(shft.baseAE, image.TFImage)
    
    assert predicted.CVImage.shape == shft.imageShape
    

def test_ShiftImageUntrainedModel():
    shft = Shift()

    images = videoToImages(f"{FERYV_STATIC_PATH}\video\default.mp4",
                          action=OBJECT_DETECTOR, **OBJECT_DETECTOR_KWARGS, interval=100)
    image = TFMultiImage(next(images))
    predicted = shft.shift(shft.baseAE, image)
    
    assert predicted.CVImage.shape == image.CVImage.shape


def test_ShiftImageTFTrainedModel():
    baseMedia: List[TFMultiImage] = []
    maskMedia: List[TFMultiImage] = []

    for image in videoToImages(f"{FERYV_STATIC_PATH}\video\default.mp4",
                            action=OBJECT_DETECTOR, **OBJECT_DETECTOR_KWARGS, interval=100):
        baseMedia.append(TFMultiImage(image))
    for image in videoToImages(f"{FERYV_STATIC_PATH}\video\default.mp4",
                            action=OBJECT_DETECTOR, **OBJECT_DETECTOR_KWARGS, interval=100):
        maskMedia.append(TFMultiImage(image))

    shft = Shift()

    baseTrainingData = np.array(list(shft.formatTrainingData(baseMedia, **OBJECT_DETECTOR_KWARGS)))
    maskTrainingData = np.array(list(shft.formatTrainingData(maskMedia, **OBJECT_DETECTOR_KWARGS)))
    
    shft.compile()
    
    shft.baseAE.fit(baseTrainingData, baseTrainingData, batch_size=16, epochs=1)
    shft.maskAE.fit(maskTrainingData, maskTrainingData, batch_size=16, epochs=1)

    images = videoToImages(f"{FERYV_STATIC_PATH}\video\default.mp4",
                          action=OBJECT_DETECTOR, **OBJECT_DETECTOR_KWARGS, interval=100)
    image = TFMultiImage(next(images))
    predicted = shft.shift(shft.baseAE, image)
    
    assert predicted.CVImage.shape == image.CVImage.shape


def test_ShiftImageLoadedModel():
    shft = Shift()

    shft.load(encoderPath=f"{SHIFT_STATIC_PATH}\shift\PTM\Encoder\Encoder",
              basePath=f"{SHIFT_STATIC_PATH}\shift\PTM\Decoder\Decoder",
              maskPath=f"{SHIFT_STATIC_PATH}\shift\PTM\Decoder\Decoder")

    images = videoToImages(f"{FERYV_STATIC_PATH}\video\default.mp4",
                          action=OBJECT_DETECTOR, **OBJECT_DETECTOR_KWARGS, interval=100)
    image = TFMultiImage(next(images))
    predicted = shft.shift(shft.baseAE, image)
    
    assert predicted.CVImage.shape == image.CVImage.shape


def test_ShiftImageTFTrainedLoadedModel():
    baseMedia: List[TFMultiImage] = []
    maskMedia: List[TFMultiImage] = []

    for image in videoToImages(f"{FERYV_STATIC_PATH}\video\default.mp4",
                            action=OBJECT_DETECTOR, **OBJECT_DETECTOR_KWARGS, interval=100):
        baseMedia.append(TFMultiImage(image))
    for image in videoToImages(f"{FERYV_STATIC_PATH}\video\default.mp4",
                            action=OBJECT_DETECTOR, **OBJECT_DETECTOR_KWARGS, interval=100):
        maskMedia.append(TFMultiImage(image))

    shft = Shift()
    
    shft.load(encoderPath=f"{SHIFT_STATIC_PATH}\shift\PTM\Encoder\Encoder",
              basePath=f"{SHIFT_STATIC_PATH}\shift\PTM\Decoder\Decoder",
              maskPath=f"{SHIFT_STATIC_PATH}\shift\PTM\Decoder\Decoder")

    baseTrainingData = np.array(list(shft.formatTrainingData(baseMedia, **OBJECT_DETECTOR_KWARGS)))
    maskTrainingData = np.array(list(shft.formatTrainingData(maskMedia, **OBJECT_DETECTOR_KWARGS)))
    
    shft.compile()
    
    shft.baseAE.fit(baseTrainingData, baseTrainingData, batch_size=16, epochs=1)
    shft.maskAE.fit(maskTrainingData, maskTrainingData, batch_size=16, epochs=1)

    images = videoToImages(f"{FERYV_STATIC_PATH}\video\default.mp4",
                          action=OBJECT_DETECTOR, **OBJECT_DETECTOR_KWARGS, interval=100)
    image = TFMultiImage(next(images))
    predicted = shft.shift(shft.baseAE, image)
    
    assert predicted.CVImage.shape == image.CVImage.shape
