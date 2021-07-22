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
from src.utils.video import loadVideo, videoToImages
from src.utils.MultiImage import MultiImage
from src.utils.detection import detectObject
from src.utils.math import getLargestRectangle
from src.variables.constants import OBJECT_DETECTOR_KWARGS, OBJECT_DETECTOR


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
    baseMedia: List[MultiImage] = []
    maskMedia: List[MultiImage] = []

    for image in videoToImages(r"src\static\video\default.mp4",
                            action=OBJECT_DETECTOR, **OBJECT_DETECTOR_KWARGS, interval=100):
        baseMedia.append(MultiImage(image))
    for image in videoToImages(r"src\static\video\default.mp4",
                            action=OBJECT_DETECTOR, **OBJECT_DETECTOR_KWARGS, interval=100):
        maskMedia.append(MultiImage(image))

    shft = Shift()

    baseTrainingData = list(shft.formatTrainingData(baseMedia, **OBJECT_DETECTOR_KWARGS))
    maskTrainingData = list(shft.formatTrainingData(maskMedia, **OBJECT_DETECTOR_KWARGS))
    
    assert baseTrainingData[0].shape == shft.imageShape
    assert maskTrainingData[0].shape == shft.imageShape


def test_LoadModel():
    shft = Shift()

    shft.load(encoderPath=r"src\static\shift\PTM\Encoder\Encoder",
              basePath=r"src\static\shift\PTM\Decoder\Decoder",
              maskPath=r"src\static\shift\PTM\Decoder\Decoder")


def test_Compile():
    shft = Shift()
    shft.compile()
    
    assert isinstance(shft, Shift)


def test_TFTraining():
    baseMedia: List[MultiImage] = []
    maskMedia: List[MultiImage] = []

    for image in videoToImages(r"src\static\video\default.mp4",
                            action=OBJECT_DETECTOR, **OBJECT_DETECTOR_KWARGS, interval=100):
        baseMedia.append(MultiImage(image))
    for image in videoToImages(r"src\static\video\default.mp4",
                            action=OBJECT_DETECTOR, **OBJECT_DETECTOR_KWARGS, interval=100):
        maskMedia.append(MultiImage(image))

    shft = Shift()

    baseTrainingData = np.array(list(shft.formatTrainingData(baseMedia, **OBJECT_DETECTOR_KWARGS)))
    maskTrainingData = np.array(list(shft.formatTrainingData(maskMedia, **OBJECT_DETECTOR_KWARGS)))
    
    shft.compile()
    
    shft.baseAE.fit(baseTrainingData, baseTrainingData, batch_size=16, epochs=1)
    shft.maskAE.fit(maskTrainingData, maskTrainingData, batch_size=16, epochs=1)


def test_TFTrainingLoadedModel():
    baseMedia: List[MultiImage] = []
    maskMedia: List[MultiImage] = []

    for image in videoToImages(r"src\static\video\default.mp4",
                            action=OBJECT_DETECTOR, **OBJECT_DETECTOR_KWARGS, interval=100):
        baseMedia.append(MultiImage(image))
    for image in videoToImages(r"src\static\video\default.mp4",
                            action=OBJECT_DETECTOR, **OBJECT_DETECTOR_KWARGS, interval=100):
        maskMedia.append(MultiImage(image))

    shft = Shift()
    
    shft.load(encoderPath=r"src\static\shift\PTM\Encoder\Encoder",
              basePath=r"src\static\shift\PTM\Decoder\Decoder",
              maskPath=r"src\static\shift\PTM\Decoder\Decoder")

    baseTrainingData = np.array(list(shft.formatTrainingData(baseMedia, **OBJECT_DETECTOR_KWARGS)))
    maskTrainingData = np.array(list(shft.formatTrainingData(maskMedia, **OBJECT_DETECTOR_KWARGS)))
    
    shft.compile()
    
    shft.baseAE.fit(baseTrainingData, baseTrainingData, batch_size=16, epochs=1)
    shft.maskAE.fit(maskTrainingData, maskTrainingData, batch_size=16, epochs=1)


def test_PredictUntrainedModel():
    shft = Shift()

    images = videoToImages(r"src\static\video\default.mp4",
                          action=OBJECT_DETECTOR, **OBJECT_DETECTOR_KWARGS, interval=100)
    image = MultiImage(next(images))
    objects = detectObject(OBJECT_DETECTOR, image=image.CVImage, **OBJECT_DETECTOR_KWARGS)
    image.crop(getLargestRectangle(objects))
    image.resize(width=shft.imageShape[0], height=shft.imageShape[1])
    
    predicted = shft.inference(shft.baseAE, image.TFImage)
    
    assert predicted.CVImage.shape == shft.imageShape


def test_PredictTFTrainedModel():
    baseMedia: List[MultiImage] = []
    maskMedia: List[MultiImage] = []

    for image in videoToImages(r"src\static\video\default.mp4",
                            action=OBJECT_DETECTOR, **OBJECT_DETECTOR_KWARGS, interval=100):
        baseMedia.append(MultiImage(image))
    for image in videoToImages(r"src\static\video\default.mp4",
                            action=OBJECT_DETECTOR, **OBJECT_DETECTOR_KWARGS, interval=100):
        maskMedia.append(MultiImage(image))

    shft = Shift()

    baseTrainingData = np.array(list(shft.formatTrainingData(baseMedia, **OBJECT_DETECTOR_KWARGS)))
    maskTrainingData = np.array(list(shft.formatTrainingData(maskMedia, **OBJECT_DETECTOR_KWARGS)))
    
    shft.compile()
    
    shft.baseAE.fit(baseTrainingData, baseTrainingData, batch_size=16, epochs=1)
    shft.maskAE.fit(maskTrainingData, maskTrainingData, batch_size=16, epochs=1)

    images = videoToImages(r"src\static\video\default.mp4",
                          action=OBJECT_DETECTOR, **OBJECT_DETECTOR_KWARGS, interval=100)
    image = MultiImage(next(images))
    objects = detectObject(OBJECT_DETECTOR, image=image.CVImage, **OBJECT_DETECTOR_KWARGS)
    image.crop(getLargestRectangle(objects))
    image.resize(width=shft.imageShape[0], height=shft.imageShape[1])
    
    predicted = shft.inference(shft.baseAE, image.TFImage)
    
    assert predicted.CVImage.shape == shft.imageShape


def test_PredictLoadedModel():
    shft = Shift()

    shft.load(encoderPath=r"src\static\shift\PTM\Encoder\Encoder",
              basePath=r"src\static\shift\PTM\Decoder\Decoder",
              maskPath=r"src\static\shift\PTM\Decoder\Decoder")

    images = videoToImages(r"src\static\video\default.mp4",
                          action=OBJECT_DETECTOR, **OBJECT_DETECTOR_KWARGS, interval=100)
    image = MultiImage(next(images))
    objects = detectObject(OBJECT_DETECTOR, image=image.CVImage, **OBJECT_DETECTOR_KWARGS)
    image.crop(getLargestRectangle(objects))
    image.resize(width=shft.imageShape[0], height=shft.imageShape[1])
    
    predicted = shft.inference(shft.baseAE, image.TFImage)
    
    assert predicted.CVImage.shape == shft.imageShape


def test_PredictTFTrainedLoadedModel():
    baseMedia: List[MultiImage] = []
    maskMedia: List[MultiImage] = []

    for image in videoToImages(r"src\static\video\default.mp4",
                            action=OBJECT_DETECTOR, **OBJECT_DETECTOR_KWARGS, interval=100):
        baseMedia.append(MultiImage(image))
    for image in videoToImages(r"src\static\video\default.mp4",
                            action=OBJECT_DETECTOR, **OBJECT_DETECTOR_KWARGS, interval=100):
        maskMedia.append(MultiImage(image))

    shft = Shift()
    
    shft.load(encoderPath=r"src\static\shift\PTM\Encoder\Encoder",
              basePath=r"src\static\shift\PTM\Decoder\Decoder",
              maskPath=r"src\static\shift\PTM\Decoder\Decoder")

    baseTrainingData = np.array(list(shft.formatTrainingData(baseMedia, **OBJECT_DETECTOR_KWARGS)))
    maskTrainingData = np.array(list(shft.formatTrainingData(maskMedia, **OBJECT_DETECTOR_KWARGS)))
    
    shft.compile()
    
    shft.baseAE.fit(baseTrainingData, baseTrainingData, batch_size=16, epochs=1)
    shft.maskAE.fit(maskTrainingData, maskTrainingData, batch_size=16, epochs=1)

    images = videoToImages(r"src\static\video\default.mp4",
                          action=OBJECT_DETECTOR, **OBJECT_DETECTOR_KWARGS, interval=100)
    image = MultiImage(next(images))
    objects = detectObject(OBJECT_DETECTOR, image=image.CVImage, **OBJECT_DETECTOR_KWARGS)
    image.crop(getLargestRectangle(objects))
    image.resize(width=shft.imageShape[0], height=shft.imageShape[1])
    
    predicted = shft.inference(shft.baseAE, image.TFImage)
    
    assert predicted.CVImage.shape == shft.imageShape
    

def test_ShiftImageUntrainedModel():
    shft = Shift()

    images = videoToImages(r"src\static\video\default.mp4",
                          action=OBJECT_DETECTOR, **OBJECT_DETECTOR_KWARGS, interval=100)
    image = MultiImage(next(images))
    predicted = shft.shift(shft.baseAE, image)
    
    assert predicted.CVImage.shape == image.CVImage.shape


def test_ShiftImageTFTrainedModel():
    baseMedia: List[MultiImage] = []
    maskMedia: List[MultiImage] = []

    for image in videoToImages(r"src\static\video\default.mp4",
                            action=OBJECT_DETECTOR, **OBJECT_DETECTOR_KWARGS, interval=100):
        baseMedia.append(MultiImage(image))
    for image in videoToImages(r"src\static\video\default.mp4",
                            action=OBJECT_DETECTOR, **OBJECT_DETECTOR_KWARGS, interval=100):
        maskMedia.append(MultiImage(image))

    shft = Shift()

    baseTrainingData = np.array(list(shft.formatTrainingData(baseMedia, **OBJECT_DETECTOR_KWARGS)))
    maskTrainingData = np.array(list(shft.formatTrainingData(maskMedia, **OBJECT_DETECTOR_KWARGS)))
    
    shft.compile()
    
    shft.baseAE.fit(baseTrainingData, baseTrainingData, batch_size=16, epochs=1)
    shft.maskAE.fit(maskTrainingData, maskTrainingData, batch_size=16, epochs=1)

    images = videoToImages(r"src\static\video\default.mp4",
                          action=OBJECT_DETECTOR, **OBJECT_DETECTOR_KWARGS, interval=100)
    image = MultiImage(next(images))
    predicted = shft.shift(shft.baseAE, image)
    
    assert predicted.CVImage.shape == image.CVImage.shape


def test_ShiftImageLoadedModel():
    shft = Shift()

    shft.load(encoderPath=r"src\static\shift\PTM\Encoder\Encoder",
              basePath=r"src\static\shift\PTM\Decoder\Decoder",
              maskPath=r"src\static\shift\PTM\Decoder\Decoder")

    images = videoToImages(r"src\static\video\default.mp4",
                          action=OBJECT_DETECTOR, **OBJECT_DETECTOR_KWARGS, interval=100)
    image = MultiImage(next(images))
    predicted = shft.shift(shft.baseAE, image)
    
    assert predicted.CVImage.shape == image.CVImage.shape


def test_ShiftImageTFTrainedLoadedModel():
    baseMedia: List[MultiImage] = []
    maskMedia: List[MultiImage] = []

    for image in videoToImages(r"src\static\video\default.mp4",
                            action=OBJECT_DETECTOR, **OBJECT_DETECTOR_KWARGS, interval=100):
        baseMedia.append(MultiImage(image))
    for image in videoToImages(r"src\static\video\default.mp4",
                            action=OBJECT_DETECTOR, **OBJECT_DETECTOR_KWARGS, interval=100):
        maskMedia.append(MultiImage(image))

    shft = Shift()
    
    shft.load(encoderPath=r"src\static\shift\PTM\Encoder\Encoder",
              basePath=r"src\static\shift\PTM\Decoder\Decoder",
              maskPath=r"src\static\shift\PTM\Decoder\Decoder")

    baseTrainingData = np.array(list(shft.formatTrainingData(baseMedia, **OBJECT_DETECTOR_KWARGS)))
    maskTrainingData = np.array(list(shft.formatTrainingData(maskMedia, **OBJECT_DETECTOR_KWARGS)))
    
    shft.compile()
    
    shft.baseAE.fit(baseTrainingData, baseTrainingData, batch_size=16, epochs=1)
    shft.maskAE.fit(maskTrainingData, maskTrainingData, batch_size=16, epochs=1)

    images = videoToImages(r"src\static\video\default.mp4",
                          action=OBJECT_DETECTOR, **OBJECT_DETECTOR_KWARGS, interval=100)
    image = MultiImage(next(images))
    predicted = shft.shift(shft.baseAE, image)
    
    assert predicted.CVImage.shape == image.CVImage.shape
