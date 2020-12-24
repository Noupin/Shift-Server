#pylint: disable=C0103, C0301, R0902
"""
The master file for the Shift application
"""
__author__ = "Noupin"

#Third Party Imports
import os
import numpy as np
import tensorflow as tf

#First Party Imports
from AI.encoder import Encoder
from AI.decoder import Decoder
from AI.autoencoder import AutoEncoder
from utils.detection import detectObject
from utils.math import getLargestRectangle
from utils.image import (resizeImage, blendImageAndColor,
                         flipImage, cropImage)


class Shift:
    """
    Two custom built AutoEncoder TensorFlow models for Shifting objects within an image.
    """

    def __init__(self, imageShape=(256, 256, 3), latentSpaceDimension=512, latentReshape=(128, 128, 3),
                       optimizer=tf.optimizers.Adam(), loss=tf.losses.mean_absolute_error, name="Default",
                       convolutionFilters=24, codingLayers=1):
        
        self.imageShape = imageShape
        self.latentSpaceDimension = latentSpaceDimension
        self.convolutionFilters = convolutionFilters

        self.codingLayers = codingLayers
        if self.codingLayers == -1:
            self.getMaxCodingLayers()
        
        latentReshapeX = int(imageShape[0]/(2**(self.codingLayers+1)))
        latentReshapeY = int(imageShape[1]/(2**(self.codingLayers+1)))


        self.encoder = Encoder(inputShape=imageShape, outputDimension=latentSpaceDimension)

        self.baseDecoder = Decoder(inputShape=(latentSpaceDimension,), latentReshape=(latentReshapeX, latentReshapeY, 24))
        self.maskDecoder = Decoder(inputShape=(latentSpaceDimension,), latentReshape=(latentReshapeX, latentReshapeY, 24))

        self.addCodingLayers(self.codingLayers)

        self.baseAE = AutoEncoder(inputShape=imageShape, encoder=self.encoder, decoder=self.baseDecoder,
                                  optimizer=optimizer, loss=loss)
        self.maskAE = AutoEncoder(inputShape=imageShape, encoder=self.encoder, decoder=self.maskDecoder,
                                  optimizer=optimizer, loss=loss)


    def getMaxCodingLayers(self):
        self.codingLayers = 1
        while (self.imageShape[0]/(2**(self.codingLayers+1)))*(self.imageShape[1]/(2**(self.codingLayers+1)))*self.convolutionFilters > self.latentSpaceDimension:
            self.codingLayers += 1
        self.codingLayers -= 1


    def formatTrainingData(self, images, objectClassifier, **kwargs):
        trainingData = []

        for image in images:
            objects = detectObject(objectClassifier, image=image, **kwargs)
            if type(objects) != tuple:
                image = resizeImage(cropImage(image, getLargestRectangle(objects)), (self.imageShape[0], self.imageShape[1]), keepAR=False)
                for ccode in range(5):
                    trainingData.append(blendImageAndColor(image, ccode))
                    for fcode in ["x", "y"]:
                        trainingData.append(flipImage(blendImageAndColor(image, ccode), fcode))
                trainingData.append(image)

        trainingData = np.array(trainingData).reshape(-1, self.imageShape[0], self.imageShape[1], self.imageShape[2])
        trainingData = trainingData.astype('float32') / 255.

        return trainingData
    

    def addCodingLayers(self, count):
        for _ in range(count):
            self.encoder.addEncodingLayer(filters=self.convolutionFilters)
            self.baseDecoder.addDecodingLayer(filters=self.convolutionFilters)
            self.maskDecoder.addDecodingLayer(filters=self.convolutionFilters)
    

    def predict(self, model, image):
        image = model.predict(image.reshape(1, self.imageShape[0], self.imageShape[1], self.imageShape[2]))
        image = image[0].reshape(self.imageShape[0], self.imageShape[1], self.imageShape[2])

        return image
    

    def build(self):
        self.encoder.buildModel()
        self.baseDecoder.buildModel()
        self.maskDecoder.buildModel()
        self.baseAE.buildModel()
        self.maskAE.buildModel()