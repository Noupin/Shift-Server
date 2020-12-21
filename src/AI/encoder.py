#pylint: disable=C0103, C0301, R0903
"""
The custom encoder class for Shift
"""
__author__ = "Noupin"

#Third Party Imports
import os
import tensorflow as tf
from colorama import Fore

#First Party Imports
from AI.TFModel import TFModel
from Exceptions.LayerIndexOutOfRange import LayerIndexOutOfRangeError


class Encoder(TFModel):
    """
    The custom built encoder layer for Shift.
    """

    def __init__(self, inputShape=(256, 256, 3), inputName="InputImage",
                       outputDimension=512, outputName="LatentOutput", outputActivation=tf.nn.relu,
                       name="Encoder"):
        super(Encoder, self).__init__(inputLayer=tf.keras.layers.Input(shape=inputShape, name=inputName),
                                      outputLayer=tf.keras.layers.Dense(outputDimension, activation=tf.nn.relu, name=outputName),
                                      name=name)
     
        self.encodingLayers = 0
        
        self.addEncodingLayer()
        self.addLayer(tf.keras.layers.Flatten(), -1)


    def addEncodingLayer(self, convFilters=5, convFilterSize=(3, 3), activation=tf.nn.relu, poolSize=(2,2), index=-1):
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
            poolSize (tuple of int, optional): The factor by which the x and y dimensions
                                               will be divided by. Defaults to (2, 2).
            index (int, optional): The position to insert the convolutional then max
                                   pooling layer. Defaults to -1.
        """

        if abs(index) > len(self.modelLayers) -1 or abs(index) < 1:
            raise LayerIndexOutOfRangeError(index, len(self.modelLayers) - 1)

        if index > 0:
            index = -(len(self.modelLayers)-index)
        self.addLayer(tf.keras.layers.Conv2D(convFilters, convFilterSize, activation=activation, padding="same"), index)
        self.addLayer(tf.keras.layers.MaxPooling2D(poolSize), index)

        self.encodingLayers += 1
