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
from src.AI.encoder import Encoder
from src.AI.decoder import Decoder
from src.utils.video import videoToImages
from src.AI.autoencoder import AutoEncoder
from src.utils.detection import detectObject
from src.constants import FILE_NAME_BYTE_SIZE, VIDEO_FRAME_GRAB_INTERVAL
from src.utils.files import generateUniqueFilename, getMediaType
from src.utils.math import getLargestRectangle, flattenList
from src.utils.image import (resizeImage, blendImageAndColor,
                             flipImage, cropImage, loadImage)


class Shift:
    """
    Two custom built AutoEncoder TensorFlow models for Shifting objects within an image.

    Args:
        id_ (str): A unique identifier for the shift model. Defaults to generateUniqueFilename(FILE_NAME_BYTE_SIZE).
        imageShape (tuple of int, optional): The resolution and color channels for the input image. Defaults to (256, 256, 3).
        latentSpaceDimension (int, optional): The dimensionality of the latent space for the compression. Defaults to 512.
        latentReshape (tuple of int, optional): The shape to reshape the latent space into. Defaults to (128, 128, 3).
        optimizer (tf.optimizers.Optimizer, optional): The optimizer to use when compiling the model. Defaults to tf.optimizers.Adam().
        loss (function, optional): The loss function to use when compiling the model. Defaults to tf.losses.mean_absolute_error.
        convolutionFilters (int, optional): The amount of filters for the coding layers. Defaults to 24.
        codingLayers (int, optional): The number of coding layers to add to the encoder and decoders. Defaults to 1.
        name (str, optional): The name of the model. Defaults to "Default".
    """

    def __init__(self, id_=generateUniqueFilename(),
                       imageShape=(256, 256, 3), latentSpaceDimension=512, latentReshape=(128, 128, 3),
                       optimizer=tf.optimizers.Adam(), loss=tf.losses.mean_absolute_error,
                       convolutionFilters=24, codingLayers=-1, name="Default"):
        self.id_ = id_
        self.imageShape = imageShape
        self.latentSpaceDimension = latentSpaceDimension
        self.convolutionFilters = convolutionFilters
        self.optimizer = optimizer
        self.loss = loss

        self.codingLayers = codingLayers
        if self.codingLayers < 0:
            self.getMaxCodingLayers()
        
        latentReshapeX = int(imageShape[0]/(2**(self.codingLayers+1)))
        latentReshapeY = int(imageShape[1]/(2**(self.codingLayers+1)))


        self.encoder = Encoder(inputShape=self.imageShape, outputDimension=latentSpaceDimension)

        self.baseDecoder = Decoder(inputShape=(latentSpaceDimension,), latentReshape=(latentReshapeX, latentReshapeY, 24))
        self.maskDecoder = Decoder(inputShape=(latentSpaceDimension,), latentReshape=(latentReshapeX, latentReshapeY, 24))

        self.addCodingLayers(self.codingLayers)

        self.baseAE = AutoEncoder(inputShape=imageShape, encoder=self.encoder, decoder=self.baseDecoder,
                                  optimizer=optimizer, loss=loss)
        self.maskAE = AutoEncoder(inputShape=imageShape, encoder=self.encoder, decoder=self.maskDecoder,
                                  optimizer=optimizer, loss=loss)
        self.shifter = AutoEncoder()


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
    

    def build(self) -> None:
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
    

    def compile(self) -> None:
        """
        Compiles all the models to be trained.
        """

        self.encoder.compileModel()
        self.baseDecoder.compileModel()
        self.maskDecoder.compileModel()
        self.baseAE.compileModel()
        self.maskAE.compileModel()
    
    
    def load(self, encoderPath: str, basePath: str, maskPath: str) -> None:
        """
        Loads the encoder and the base and mask decoder then creates the autoencoders to be trained.

        Args:
            encoderPath (str): The path to the encoder to be loaded
            basePath (str): The path to the base decoder to be loaded
            maskPath (str): The path to the mask decoder to be loaded
        """

        if encoderPath:
            self.encoder = tf.keras.models.load_model(encoderPath)

        if basePath:
            self.baseDecoder = tf.keras.models.load_model(basePath)
        if maskPath:
            self.maskDecoder = tf.keras.models.load_model(maskPath)

        self.baseAE = AutoEncoder(inputShape=self.imageShape, encoder=self.encoder, decoder=self.baseDecoder,
                                  optimizer=self.optimizer, loss=self.loss)
        self.maskAE = AutoEncoder(inputShape=self.imageShape, encoder=self.encoder, decoder=self.maskDecoder,
                                  optimizer=self.optimizer, loss=self.loss)
    

    def loadData(imageType: str, dataPath: str) -> List[np.ndarray]:
        """
        Loads the images and videos for either the mask or base model

        Args:
            imageType (str): Either 'mask' or 'base' to load the correct files
            dataPath (str): The path to the folder holding the data

        Returns:
            list of np.ndarray: The images to load in
        """
        
        loadedImages = []
        files = os.listdir(dataPath)
        print(files)
        for media in files:
            if media.find(imageType) == -1:
                continue

            mediaType = getMediaType(dataPath)

            if mediaType == 'video':
                loadedImages += videoToImages(media, interval=VIDEO_FRAME_GRAB_INTERVAL)
            elif mediaType == "image":
                loadedImages.append(loadImage(media))
        
        return loadedImages
    

    def save(self, encoderPath: str, basePath: str, maskPath: str) -> None:
        """
        Saves the encoder and both of the decoders to the given paths

        Args:
            encoderPath (str): The path to save self.encoder to
            basePath (str): The path to save self.baseDecoder to
            maskPath (str): The path to save self.maskDecoder to
        """

        self.encoder.save(os.path.join(encoderPath, f"encoder"))
        self.baseDecoder.save(os.path.join(basePath, f"baseDecoder"))
        self.maskDecoder.save(os.path.join(maskPath, f"maskDecoder"))
