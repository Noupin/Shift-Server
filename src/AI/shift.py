#pylint: disable=C0103, C0301, R0902
"""
The master file for the Shift application
"""
__author__ = "Noupin"

#Third Party Imports
import os
import random
import numpy as np
import tensorflow as tf
from typing import List

#First Party Imports
from AI.encoder import Encoder
from AI.decoder import Decoder
from AI.autoencoder import AutoEncoder
from utils.detection import detectObject
from utils.math import getLargestRectangle, flattenList
from utils.image import (resizeImage, blendImageAndColor,
                         flipImage, cropImage)


class Shift:
    """
    Two custom built AutoEncoder TensorFlow models for Shifting objects within an image.

    Args:
        imageShape (tuple of int, optional): [description]. Defaults to (256, 256, 3).
        latentSpaceDimension (int, optional): [description]. Defaults to 512.
        latentReshape (tuple of int, optional): [description]. Defaults to (128, 128, 3).
        optimizer (tf.optimizers.Optimizer, optional): [description]. Defaults to tf.optimizers.Adam().
        loss (function, optional): [description]. Defaults to tf.losses.mean_absolute_error.
        name (str, optional): [description]. Defaults to "Default".
        convolutionFilters (int, optional): [description]. Defaults to 24.
        codingLayers (int, optional): [description]. Defaults to 1.
    """

    def __init__(self, imageShape=(256, 256, 3), latentSpaceDimension=512, latentReshape=(128, 128, 3),
                       optimizer=tf.optimizers.Adam(), loss=tf.losses.mean_absolute_error, name="Default",
                       convolutionFilters=24, codingLayers=-1):
        self.imageShape = imageShape
        self.latentSpaceDimension = latentSpaceDimension
        self.convolutionFilters = convolutionFilters

        self.codingLayers = codingLayers
        if self.codingLayers < 0:
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


    def getMaxCodingLayers(self) -> None:
        """
        Depending on the incoming resolution of the image and the latent space dimensionality
        the maximum number of coding layers will be found while keeping the magnitude of the
        output of the final convolution above the magnitude of the latent space dimension.
        """

        self.codingLayers = 1
        while (self.imageShape[0]/(2**(self.codingLayers+1)))*(self.imageShape[1]/(2**(self.codingLayers+1)))*self.convolutionFilters > self.latentSpaceDimension:
            self.codingLayers += 1
        self.codingLayers -= 1


    def formatTrainingData(self, images: List[np.ndarray], objectClassifier, flipCodes=["y"], **kwargs) -> List[np.ndarray]:
        """
        Formats and shuffles images with objectClassifier ready to train the Shift models.

        Args:
            images (list of numpy.ndarray): The images to be formatted for Shift model training
            objectClassifier (function): The function used as a classifier on the images
            flipCodes (list of str): The codes to flip the image for augmentation. Defaults to ["x"].
            **kwargs: The key word arguments to pass into detectObject function

        Returns:
            list of numpy.ndarray: The list of training images ready to be input to the Shift models
        """

        trainingData = []

        for image in images:
            objects = detectObject(objectClassifier, image=image, **kwargs)
            if type(objects) != tuple:
                augmented = []
                augmentedItems = 0
                image = resizeImage(cropImage(image, getLargestRectangle(objects)), (self.imageShape[0], self.imageShape[1]), keepAR=False)
                
                coloredImages = [image]
                for colorCode in range(5):
                    coloredImages.append(blendImageAndColor(image, colorCode))

                randomColored = coloredImages.copy()
                random.shuffle(randomColored)
                augmentedItems += len(randomColored)
                augmented.append(randomColored)

                for flipCode in flipCodes:
                    flippedImages = []
                    for coloredImage in coloredImages:
                        flippedImages.append(flipImage(coloredImage, flipCode))

                    random.shuffle(flippedImages)
                    augmentedItems += len(flippedImages)
                    augmented.append(flippedImages)

                shuffledAugmented = random.sample(flattenList(augmented), augmentedItems)
                trainingData.append(shuffledAugmented)

        random.shuffle(trainingData)
        trainingData = np.array(flattenList(trainingData)).reshape(-1, self.imageShape[0], self.imageShape[1], self.imageShape[2])
        trainingData = trainingData.astype('float32') / 255.

        return trainingData
    

    def addCodingLayers(self, count: int) -> None:
        """
        Adds count encoding and decoding layers to the encoder and each of the decoders.

        Args:
            count (int): The number of encoding and decoding layers to add
        """

        for _ in range(count):
            self.encoder.addEncodingLayer(filters=self.convolutionFilters)
            self.baseDecoder.addDecodingLayer(filters=self.convolutionFilters)
            self.maskDecoder.addDecodingLayer(filters=self.convolutionFilters)
    

    def predict(self, model: tf.keras.Model, image: np.ndarray) -> np.ndarray:
        """
        Uses model to predict on image

        Args:
            model (tf.keras.Model): The model to be used for inferencing
            image (numpy.ndarray): The image to be inferenced on

        Returns:
            numpy.ndarray: The predicted image
        """

        image = model.predict(image.reshape(1, self.imageShape[0], self.imageShape[1], self.imageShape[2]))
        image = image[0].reshape(self.imageShape[0], self.imageShape[1], self.imageShape[2])

        return image
    

    def build(self):
        """
        Builds each of the models used in Shift. Building a model can only happen once
        and will raise an error if done multiple times. Building is helpful when using
        .summary() but not needed.
        """

        self.encoder.buildModel()
        self.baseDecoder.buildModel()
        self.maskDecoder.buildModel()
        self.baseAE.buildModel()
        self.maskAE.buildModel()