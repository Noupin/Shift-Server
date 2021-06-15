#pylint: disable=C0103, C0301, R0902
"""
The Shift AI for the Shift application
"""
__author__ = "Noupin"

#Third Party Imports
import os
import moviepy
import numpy as np
import tensorflow as tf
from flask import current_app
from typing import List, Union, Generator
from moviepy import editor as mediaEditor

#First Party Imports
from src.AI.TFModel import TFModel
from src.AI.Encoder import Encoder
from src.AI.Decoder import Decoder
from src.utils.video import videoToImages
from src.AI.Autoencoder import Autoencoder
from src.utils.memory import chunkIterable
from src.utils.MultiImage import MultiImage
from src.utils.math import getLargestRectangle, flattenList
from src.utils.files import generateUniqueFilename, getMediaType
from src.utils.detection import detectObject, getFacialLandmarks
from src.utils.image import (resizeImage, blendImageAndColor,
                             flipImage, cropImage, loadImage,
                             replaceAreaOfImage, viewImage,
                             drawPolygon, applyMask,
                             imagesToVideo)
from src.variables.constants import (OBJECT_CLASSIFIER, SHIFT_PATH,
                                     VIDEO_FRAME_GRAB_INTERVAL,
                                     HUE_ADJUSTMENT)


class Shift:
    """
    Two custom built Autoencoder TensorFlow models for Shifting objects within an image.

    Args:
        id_ (str): A unique identifier for the shift model. Defaults to generateUniqueFilename().
        imageShape (tuple of int, optional): The resolution and color channels for the input image. Defaults to (256, 256, 3).
        latentSpaceDimension (int, optional): The dimensionality of the latent space for the compression. Defaults to 512.
        latentReshape (tuple of int, optional): The shape to reshape the latent space into. Defaults to (128, 128, 3).
        optimizer (tf.optimizers.Optimizer, optional): The optimizer to use when compiling the model. Defaults to tf.optimizers.Adam().
        loss (function, optional): The loss function to use when compiling the model. Defaults to tf.losses.mean_absolute_error.
        convolutionFilters (int, optional): The amount of filters for the coding layers. Defaults to 24.
        codingLayers (int, optional): The number of coding layers to add to the encoder and decoders. Defaults to 1.
    """

    def __init__(self, id_=generateUniqueFilename()[1],
                       imageShape=(256, 256, 3), latentSpaceDimension=512, latentReshape=(128, 128, 3),
                       optimizer=tf.optimizers.Adam(), loss=tf.losses.mean_absolute_error,
                       convolutionFilters=24, codingLayers=-1):
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


        self.encoder: TFModel = Encoder(inputShape=self.imageShape, outputDimension=latentSpaceDimension)

        self.baseDecoder: TFModel = Decoder(inputShape=(latentSpaceDimension,), latentReshape=(latentReshapeX, latentReshapeY, 24))
        self.maskDecoder: TFModel = Decoder(inputShape=(latentSpaceDimension,), latentReshape=(latentReshapeX, latentReshapeY, 24))

        self.addCodingLayers(self.codingLayers)

        #Will shift objects from mask to base if predicting on mask images
        self.baseAE: TFModel = Autoencoder(inputShape=imageShape, encoder=self.encoder, decoder=self.baseDecoder,
                                           optimizer=optimizer, loss=loss, name="Base")
        #Will shift objects from base to mask if predicting on base images
        self.maskAE: TFModel = Autoencoder(inputShape=imageShape, encoder=self.encoder, decoder=self.maskDecoder,
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


    def formatTrainingData(self, images: Union[Generator[MultiImage, None, None], List[MultiImage]], objectClassifier=OBJECT_CLASSIFIER,
                           flipCodes=["y"], **kwargs) -> Generator[np.ndarray, None, None]:
        """
        Formats and shuffles images with objectClassifier ready to train the Shift models. Converts \
        images from MultiImage to np.ndarray or MultiImage.CVImage.

        Args:
            images (Generator of MultiImage or list of MultiImage): The images to be formatted for Shift model training
            objectClassifier (function): The classifier used to detect the are of the image
                                         to shift. Defaults to OBJECT_CLASSIFIER.
            flipCodes (list of str): The codes to flip the image for augmentation. Defaults to ["x"].
            **kwargs: The key word arguments to pass into detectObject function

        Returns:
            list of numpy.ndarray or Generator for numpy.ndarray: The list of training images ready to be input to the Shift models
        """

        for image in images:
            objects = detectObject(objectClassifier, image=image.CVImage, **kwargs)
            if len(objects) < 1:
                continue

            image.crop(getLargestRectangle(objects))
            image.resize(self.imageShape[0], self.imageShape[1])

            for hue in HUE_ADJUSTMENT:
                huedImage = tf.image.adjust_hue(image.TFImage, hue)
                yield np.array(tf.image.adjust_hue(image.TFImage, hue))
                
                for flipCode in flipCodes:
                    yield flipImage(huedImage, flipCode)
    

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
    

    def predict(self, model: TFModel, image: np.ndarray) -> MultiImage:
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
        
        return MultiImage(image)

    
    def shiftImages(self, model: tf.keras.Model, images: Generator[MultiImage, None, None],
                    objectClassifier=OBJECT_CLASSIFIER, imageResizer=resizeImage,
                    asNumpy=False, **kwargs) -> Generator[MultiImage, None, None]:
        """
        Given an image the classifier will determine an area of the image to replace
        with the shifted object.

        Args:
            model (tf.keras.Model): The model used to shift the objects.
            images (types.GeneratorType or np.ndarray): The images to be shifted
            objectClassifier (function): The classifier used to detect the are of the image
                                         to shift. Defaults to OBJECT_CLASSIFIER.
            imageResizer (function): The function used to resize images. Defaults to resizeImage.
            asNumpy (bool, optional): Whether or not to yield np.ndarray as opposed to the default
                                      MultiImage. Defaults to False.
            **kwargs: The key word arguments to pass into detectObject function

        Yields:
            np.ndarray: The shifted image.
        """

        for image in images:
            objects = detectObject(objectClassifier, image=image.CVImage, **kwargs)

            if len(objects) < 1:
                yield image.CVImage if asNumpy else image
                continue
            
            replaceArea = getLargestRectangle(objects)
            originalCroppedImage = cropImage(image.CVImage, replaceArea)
            replaceImageXY = (originalCroppedImage.shape[0], originalCroppedImage.shape[1])

            replaceImage = MultiImage(image.CVImage)
            replaceImage.resize(self.imageShape[0], self.imageShape[1], resizer=imageResizer)
            replaceImage = self.predict(model, replaceImage.TFImage)
            replaceImage.resize(replaceImageXY[0], replaceImageXY[1], resizer=imageResizer)

            landmarks = getFacialLandmarks(image.CVImage, replaceArea)
            maskLandmarks = np.array(landmarks[17:26][::-1]+landmarks[0:16]) #Eyebrows and Jawline Landmarks
            mask = drawPolygon(image.CVImage, maskLandmarks, mask=True)
            mask = cropImage(mask, replaceArea) #Cropping the mask to fit the shifted image

            maskedImage = applyMask(originalCroppedImage, replaceImage.CVImage, mask)
            shiftedImage = replaceAreaOfImage(image.CVImage, replaceArea, maskedImage)
            
            yield shiftedImage if asNumpy else MultiImage(shiftedImage)
    

    def shift(self, model: tf.keras.Model, media: Union[Generator[MultiImage, None, None], List[MultiImage], MultiImage],
              fps=30.0, objectClassifier=OBJECT_CLASSIFIER, imageResizer=resizeImage,
              **kwargs)-> Union[mediaEditor.VideoFileClip, MultiImage]:
        """
        Shifts the desired objects in the media.

        Args:
            model (tf.keras.Model): The model used to shift the objects.
            media (generator of MultiImage or list of MultiImage or MultiImage]): The media to be shifted
            objectClassifier (function): The classifier used to detect the are of the image
                                         to shift. Defaults to OBJECT_CLASSIFIER.
            imageResizer (function): The function used to resize images. Defaults to resizeImage.
            fps (float): The fps to save the video at. Defaults to 30.0.
            **kwargs: The key word arguments to pass into detectObject function

        Returns:
            mediaEditor.VideoFileClip or MultiImage: The shifted media
        """

        isImage = False

        if isinstance(media, MultiImage) and media.CVImage.ndim == 3:
            mediaGenerator = self.shiftImages(model, [media], objectClassifier, imageResizer, **kwargs)
            isImage = True
        elif len(media) == 1 and isinstance(media[0], MultiImage) and media[0].CVImage.ndim == 3:
            mediaGenerator = self.shiftImages(model, [media[0]], objectClassifier, imageResizer, **kwargs)
            isImage = True
        else:
            mediaGenerator = self.shiftImages(model, media, objectClassifier, imageResizer, **kwargs)
            shape = next(mediaGenerator).CVImage.shape

            mediaGenerator = self.shiftImages(model, media, objectClassifier, imageResizer, asNumpy=True, **kwargs)

        if isImage:
            return next(mediaGenerator)
        else:
            return imagesToVideo(mediaGenerator, shape, os.path.join(current_app.root_path, SHIFT_PATH, self.id_, f"{str(self.id_)}.mp4"), fps)
 

    def compile(self) -> None:
        """
        Compiles all the models to be trained.
        """

        self.encoder.compileModel()
        self.baseDecoder.compileModel()
        self.maskDecoder.compileModel()
        self.baseAE.compileModel()
        self.maskAE.compileModel()
    

    def load(self, encoderPath: str=None, basePath: str = None, maskPath: str=None, absPath=False, **kwargs) -> None:
        """
        Loads the encoder and the base and mask decoder then creates the Autoencoders to be trained.

        Args:
            encoderPath (str, optional): The path to the encoder to be loaded. Defaults to None.
            basePath (str, optional): The path to the base decoder to be loaded. Defaults to None.
            maskPath (str, optional): The path to the mask decoder to be loaded. Defaults to None.
            absPath (bool, optional): Whteher or not the absolute path is given. Defaults to False.
            kwargs: Additional kwargs to be passed to the Shift.load() function.
        """

        if basePath:
            if absPath:
                self.baseDecoder.load(basePath, **kwargs)
            else:
                self.baseDecoder.load(os.path.join(basePath, f"baseDecoder", f"baseDecoder"), **kwargs)

            if not encoderPath:
                self.baseAE: TFModel = Autoencoder(inputShape=self.imageShape, encoder=self.encoder,
                                                   decoder=self.baseDecoder, optimizer=self.optimizer,
                                                   loss=self.loss, name="Base")

        if maskPath:
            if absPath:
                self.maskDecoder.load(maskPath, **kwargs)
            else:
                self.maskDecoder.load(os.path.join(maskPath, f"maskDecoder", f"maskDecoder"), **kwargs)

            if not encoderPath:
                self.maskAE: TFModel = Autoencoder(inputShape=self.imageShape, encoder=self.encoder,
                                                   decoder=self.maskDecoder, optimizer=self.optimizer,
                                                   loss=self.loss, name="Mask")
        
        if encoderPath:
            if absPath:
                self.encoder.load(encoderPath, **kwargs)
            else:
                self.encoder.load(os.path.join(encoderPath, f"encoder", f"encoder"), **kwargs)

            self.baseAE: TFModel = Autoencoder(inputShape=self.imageShape, encoder=self.encoder,
                                               decoder=self.baseDecoder, optimizer=self.optimizer,
                                               loss=self.loss, name="Base")
            self.maskAE: TFModel = Autoencoder(inputShape=self.imageShape, encoder=self.encoder,
                                               decoder=self.maskDecoder, optimizer=self.optimizer,
                                               loss=self.loss, name="Mask")

        self.compile()


    def loadData(self, dataPath: str, interval=VIDEO_FRAME_GRAB_INTERVAL, action=None, firstMedia=False,
                 firstImage=False, **kwargs) -> Generator[MultiImage, None, None]:
        """
        Loads the images and videos for either the mask or base model

        Args:
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
            Generator of MultiImage: The images to load in.
        """

        files = os.listdir(dataPath)

        for media in files:
            mediaType = getMediaType(media)

            if mediaType == 'video':
                for image in videoToImages(os.path.join(dataPath, media), interval=interval, firstImage=firstImage, action=action, **kwargs):
                    yield MultiImage(image)
            elif mediaType == "image":
                yield MultiImage(os.path.join(dataPath, media))
            
            if firstMedia:
                break
                
            if firstImage:
                break


    def save(self, encoderPath: str=None, basePath: str=None, maskPath: str=None, **kwargs) -> None:
        """
        Saves the encoder and both of the decoders to the given paths

        Args:
            encoderPath (str, optional): The path to save self.encoder to. Defaults to None.
            basePath (str, optional): The path to save self.baseDecoder to. Defaults to None.
            maskPath (str, optional): The path to save self.maskDecoder to. Defaults to None.
            kwargs: The kwargs to be passed to save_weights
        """
        
        saveFormat = 'tf'
        if kwargs.get("save_format"):
            saveFormat = kwargs.get("save_format")
            kwargs.pop("save_item")

        if encoderPath:
            self.encoder.save_weights(os.path.join(encoderPath, f"encoder", f"encoder"),
                                      save_format=saveFormat, **kwargs)
        if basePath:
            self.baseDecoder.save_weights(os.path.join(basePath, f"baseDecoder", f"baseDecoder"),
                                          save_format=saveFormat, **kwargs)
        if maskPath:
            self.maskDecoder.save_weights(os.path.join(maskPath, f"maskDecoder", f"maskDecoder"),
                                          save_format=saveFormat, **kwargs)
