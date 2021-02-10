#pylint: disable=C0103, C0301, R0902
"""
The master file for the Shift application
"""
__author__ = "Noupin"

#Third Party Imports
import os
import types
import random
import moviepy
import numpy as np
import tensorflow as tf
from typing import List, Union
from skimage.util import img_as_float

#First Party Imports
from src.AI.TFModel import TFModel
from src.AI.encoder import Encoder
from src.AI.decoder import Decoder
from src.utils.video import videoToImages
from src.AI.autoencoder import AutoEncoder
from src.utils.memory import chunkIterable
from src.utils.math import getLargestRectangle, flattenList
from src.utils.files import generateUniqueFilename, getMediaType
from src.utils.detection import detectObject, getFacialLandmarks
from src.utils.image import (resizeImage, blendImageAndColor,
                             flipImage, cropImage, loadImage,
                             replaceAreaOfImage, viewImage,
                             drawPolygon, applyMask,
                             imagesToVideo)
from src.variables.constants import (OBJECT_CLASSIFIER,
                                     VIDEO_FRAME_GRAB_INTERVAL,
                                     TEMP_MEDIA_PATH)


class Shift:
    """
    Two custom built AutoEncoder TensorFlow models for Shifting objects within an image.

    Args:
        id_ (str): A unique identifier for the shift model. Defaults to generateUniqueFilename().
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
                       convolutionFilters=24, codingLayers=-1, name="Default",
                       modelPath=""):
        self.id_ = id_[1]
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


        self.encoder: TFModel = Encoder(inputShape=self.imageShape, outputDimension=latentSpaceDimension)

        self.baseDecoder: TFModel = Decoder(inputShape=(latentSpaceDimension,), latentReshape=(latentReshapeX, latentReshapeY, 24))
        self.maskDecoder: TFModel = Decoder(inputShape=(latentSpaceDimension,), latentReshape=(latentReshapeX, latentReshapeY, 24))

        self.addCodingLayers(self.codingLayers)

        #Will shift objects from mask to base if predicting on mask images
        self.baseAE: TFModel = AutoEncoder(inputShape=imageShape, encoder=self.encoder, decoder=self.baseDecoder,
                                           optimizer=optimizer, loss=loss, name="Base")
        #Will shift objects from base to mask if predicting on base images
        self.maskAE: TFModel = AutoEncoder(inputShape=imageShape, encoder=self.encoder, decoder=self.maskDecoder,
                                           optimizer=optimizer, loss=loss, name="Mask")


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


    def formatTrainingData(self, images: types.GeneratorType, objectClassifier=OBJECT_CLASSIFIER, flipCodes=["y"], **kwargs) -> List[np.ndarray]:
        """
        Formats and shuffles images with objectClassifier ready to train the Shift models.

        Args:
            images (types.GeneratorType): The images to be formatted for Shift model training
            objectClassifier (function): The classifier used to detect the are of the image
                                         to shift. Defaults to OBJECT_CLASSIFIER.
            flipCodes (list of str): The codes to flip the image for augmentation. Defaults to ["x"].
            **kwargs: The key word arguments to pass into detectObject function

        Returns:
            list of numpy.ndarray: The list of training images ready to be input to the Shift models
        """

        trainingData = []

        for image in images:
            objects = detectObject(objectClassifier, image=image, **kwargs)
            if type(objects) == tuple:
                continue
            
            augmented = []
            augmentedItems = 0
            resized = resizeImage(cropImage(image, getLargestRectangle(objects)), (self.imageShape[0], self.imageShape[1]))
            yield (resized / 255.).astype('float32')
            #trainingData.append(resized)
            '''
            coloredImages = [resized]
            for colorCode in range(5):
                coloredImages.append(blendImageAndColor(resized, colorCode))

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
        trainingData = np.array(flattenList(trainingData)).reshape(-1, self.imageShape[0], self.imageShape[1], self.imageShape[2]) / 255.
        trainingData = trainingData.astype('float32')

        return trainingData'''
    

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
    

    def predict(self, model: TFModel, image: np.ndarray) -> np.ndarray:
        """
        Uses model to predict on image

        Args:
            model (TFModel): The model to be used for inferencing
            image (numpy.ndarray): The image to be inferenced on

        Returns:
            numpy.ndarray: The predicted image
        """

        image = model.predict(image.reshape(1, self.imageShape[0], self.imageShape[1], self.imageShape[2]))
        image = image[0].reshape(self.imageShape[0], self.imageShape[1], self.imageShape[2])

        return image

    
    def shiftMedia(self, model: tf.keras.Model, media: types.GeneratorType, objectClassifier=OBJECT_CLASSIFIER, imageResizer=resizeImage, **kwargs) -> np.ndarray:
        """
        Given an image the classifier will determine an area of the image to replace
        with the shifted object.

        Args:
            model (tf.keras.Model): The model used to shift the objects.
            media (types.GeneratorType or np.ndarray): The media to be shifted
            objectClassifier (function): The classifier used to detect the are of the image
                                         to shift. Defaults to OBJECT_CLASSIFIER.
            imageResizer (function): The function used to resize images. Defaults to resizeImage.
            **kwargs: The key word arguments to pass into detectObject function

        Yields:
            np.ndarray: The shifted image.
        """

        for image in media:
            image = image.astype(np.uint8)
            objects = detectObject(objectClassifier, image=image, **kwargs)

            if type(objects) == tuple:
                yield image
                continue
            
            replaceArea = getLargestRectangle(objects)
            originalCroppedImage = cropImage(image, replaceArea)
            replaceImageXY = (originalCroppedImage.shape[0], originalCroppedImage.shape[1])

            replaceImage = imageResizer(originalCroppedImage, (self.imageShape[0], self.imageShape[1]))
            shiftedReplace = self.predict(model, replaceImage.astype(np.float32)) #TF needs float32 not uint8
            shiftedReplace = shiftedReplace.astype(np.uint8)
            replaceImage = imageResizer(shiftedReplace, replaceImageXY)

            landmarks = getFacialLandmarks(image, replaceArea)
            maskLandmarks = np.array(landmarks[17:26][::-1]+landmarks[0:16]) #Eyebrows and Jawline Landmarks
            mask = drawPolygon(image, maskLandmarks, mask=True)
            mask = cropImage(mask, replaceArea) #Cropping the mask to fit the shifted image

            maskedImage = applyMask(originalCroppedImage, replaceImage, mask)
            shiftedImage = replaceAreaOfImage(image, replaceArea, maskedImage)
    
            yield shiftedImage
    

    def shift(self, model: tf.keras.Model, media: Union[types.GeneratorType, np.ndarray], fps=30.0, objectClassifier=OBJECT_CLASSIFIER, imageResizer=resizeImage, **kwargs) -> Union[moviepy.video.io.VideoFileClip.VideoFileClip, np.ndarray]:
        """
        Shifts the desired objects in the media.

        Args:
            model (tf.keras.Model): The model used to shift the objects.
            media (types.GeneratorType or np.ndarray): The media to be shifted
            objectClassifier (function): The classifier used to detect the are of the image
                                         to shift. Defaults to OBJECT_CLASSIFIER.
            imageResizer (function): The function used to resize images. Defaults to resizeImage.
            fps (float): The fps to save the video at. Defaults to 30.0.
            **kwargs: The key word arguments to pass into detectObject function

        Returns:
            moviepy.video.io.VideoFileClip.VideoFileClip or np.ndarray: The shifted media
        """

        isImage = False

        if isinstance(media, np.ndarray) and media.ndim == 3:
            mediaGenerator = self.shiftMedia(model, [media], objectClassifier, imageResizer, **kwargs)
            isImage = True
        else:
            mediaGenerator = self.shiftMedia(model, media, objectClassifier, imageResizer, **kwargs)
            shape = next(mediaGenerator).shape
            mediaGenerator = self.shiftMedia(model, media, objectClassifier, imageResizer, **kwargs)
        
        if isImage:
            return next(mediaGenerator)
        else:
            return imagesToVideo(mediaGenerator, shape, os.path.join(TEMP_MEDIA_PATH, f"{str(self.id_)}.mp4"), fps)
        


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
    
    
    def load(self, encoderPath: str=None, basePath: str = None, maskPath: str=None) -> None:
        """
        Loads the encoder and the base and mask decoder then creates the autoencoders to be trained.

        Args:
            encoderPath (str): The path to the encoder to be loaded
            basePath (str): The path to the base decoder to be loaded
            maskPath (str): The path to the mask decoder to be loaded
        """

        ##
        #Work Around
        ##
        if encoderPath:
            self.encoder = tf.keras.models.load_model(encoderPath)
            #self.encoder.load(encoderPath)
            #self.encoder.load_weights(encoderPath)

        if basePath:
            self.baseDecoder = tf.keras.models.load_model(basePath)
            #self.baseDecoder.load(basePath)
            #self.baseDecoder.load_weights(basePath)
            self.baseAE = AutoEncoder(inputShape=self.imageShape, encoder=self.encoder, decoder=self.baseDecoder,
                                      optimizer=self.optimizer, loss=self.loss)
        if maskPath:
            self.maskDecoder = tf.keras.models.load_model(maskPath)
            #self.maskDecoder.load(maskPath)
            #self.maskDecoder.load_weights(maskPath)
            self.maskAE = AutoEncoder(inputShape=self.imageShape, encoder=self.encoder, decoder=self.maskDecoder,
                                      optimizer=self.optimizer, loss=self.loss)
    

    def loadData(self, imageType: str, dataPath: str, interval=VIDEO_FRAME_GRAB_INTERVAL, action=None, firstMedia=False, firstImage=False, **kwargs) -> List[np.ndarray]:
        """
        Loads the images and videos for either the mask or base model

        Args:
            imageType (str): Either 'mask' or 'base' to load the correct files
            dataPath (str): The path to the folder holding the data
            interval (int): The interval to grab images from a video
            action (function): The classifier to determine whether the frame of
                               the video is valid to inference on. Defaults to
                               None.
            firstMedia (bool): Whether or not to only load the first version of
                               that media. For exmaple when delivering the final
                               shift only the first base video will want to be
                               loaded. Defaults to False.
            firstImage (bool): Whether or not to only load the first image from the
                               imageType media. Defaults to False.
            kwargs: The additional keyword arguments to pass to the action.

        Returns:
            list of np.ndarray: The images to load in.
        """
        
        loadedImages = []
        files = os.listdir(dataPath)

        for media in files:
            if media.find(imageType) == -1:
                continue

            mediaType = getMediaType(media)

            if mediaType == 'video':
                loadedImages += videoToImages(os.path.join(dataPath, media), interval=interval, firstImage=firstImage, action=action, **kwargs)
            elif mediaType == "image":
                loadedImages.append(loadImage(os.path.join(dataPath, media)))
            
            if firstMedia:
                break
                
            if firstImage:
                break
        
        return loadedImages
    

    def save(self, encoderPath: str, basePath: str, maskPath: str) -> None:
        """
        Saves the encoder and both of the decoders to the given paths

        Args:
            encoderPath (str): The path to save self.encoder to
            basePath (str): The path to save self.baseDecoder to
            maskPath (str): The path to save self.maskDecoder to
        """

        if encoderPath:
            self.encoder.save(os.path.join(encoderPath, f"encoder"), save_format='tf')
        if basePath:
            self.baseDecoder.save(os.path.join(basePath, f"baseDecoder"), save_format='tf')
        if maskPath:
            self.maskDecoder.save(os.path.join(maskPath, f"maskDecoder"), save_format='tf')
