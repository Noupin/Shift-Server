#pylint: disable=C0103, C0301, R0903
"""
The custom decoder class for Shift
"""
__author__ = "Noupin"

#Third Party Imports
import os
import tensorflow as tf
from colorama import Fore

#First Party Imports
from utils.math import prod
from AI.TFModel import TFModel
from Exceptions.LayerIndexOutOfRange import LayerIndexOutOfRangeError


class Decoder(TFModel):
    """
    The custom built decoder layer for Shift.
    """

    def __init__(self, inputShape=(512,), inputName="LatentInput",
                       latentReshape=(128, 128, 3),
                       outputDimension=3, outputFilters=5, outputFilterSize=(1, 1),
                       outputName="OutputImage", outputActivation=tf.nn.relu,
                       name="Decoder"):
        super(Decoder, self).__init__(inputLayer=tf.keras.layers.Input(shape=inputShape, name=inputName),
                                      outputLayer=tf.keras.layers.Conv2D(outputDimension, outputFilters, strides=1, padding="same", name=outputName),
                                      name=name)
     
        self.decodingLayers = 0
        
        self.addLayer(tf.keras.layers.Dense(prod(latentReshape), activation=outputActivation), 1)
        self.addLayer(tf.keras.layers.Reshape(latentReshape), 2)
        self.addDecodingLayer()


    def addDecodingLayer(self, convFilters=5, convFilterSize=(3, 3), activation=tf.nn.relu, upsampSize=(2,2), index=-1):
        """
        Adds a 2D convolutional layer with convFilters convolutional filters,
        a convolutional filter size of convFilterSize and an activation
        function of activation. Then a 2D maximum pooling layer with a pooling
        size of poolSize. Both of these are added at index starting with Conv2D
        then to MaxPooling2D. Great image explanation here:
        https://miro.medium.com/max/3288/1*uAeANQIOQPqWZnnuH-VEyw.jpeg

        Args:
            convFilters (int, optional): The number of filters or layers that the convolutional
                                         layer will split into. Defaults to 5.
            convFilterSize (tuple of int, optional): The size of each of the convolutional
                                                     filters. Defaults to (3, 3).
            activation (function, optional): The activation function for the convolutional
                                             layer. Defaults to tf.nn.relu.
            upsampSize (tuple of int, optional): The factor by which the x and y dimensions
                                                 will be multiplied by. Defaults to (2, 2).
            index (int, optional): The position to insert the convolutional then max
                                   pooling layer. Defaults to -1.
        """

        if abs(index) > len(self.modelLayers) -1 or abs(index) < 1:
            raise LayerIndexOutOfRangeError(index, len(self.modelLayers) - 1)

        self.addLayer(tf.keras.layers.Conv2D(convFilters, convFilterSize, activation=activation, padding="same"), index)
        self.addLayer(tf.keras.layers.UpSampling2D(upsampSize), index)

        self.decodingLayers += 1
