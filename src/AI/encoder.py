#pylint: disable=C0103, C0301, R0903
"""
The custom Encoder model for TFModel
"""
__author__ = "Noupin"

#Third Party Imports
import os
import tensorflow as tf
from colorama import Fore

#First Party Imports
from src.AI.TFModel import TFModel
from src.Exceptions.LayerIndexOutOfRange import LayerIndexOutOfRangeError


class Encoder(TFModel):
    """
    A Base Encoder TensorFlow model for Feryv projects.

    Args:
        inputShape (tuple of int, optional): The input shape for the encoder model. Defaults to (256, 256, 3).
        inputName (str, optional): The name of the input layer. Defaults to "InputImage".
        outputDimension (int, optional): The dimensionality of the latent space. Defaults to 512.
        outputName (str, optional): The name of the output layer. Defaults to "LatentOutput".
        outputActivation (function, optional): The activation function for the output layer. Defaults to tf.nn.relu.
        name (str, optional): The name for model. Defaults to "Encoder".
    """

    def __init__(self, inputShape=(256, 256, 3), inputName="InputImage",
                       outputDimension=512, outputName="LatentOutput", outputActivation=tf.nn.relu,
                       name="Encoder", modelPath=""):
        super(Encoder, self).__init__(inputShape=inputShape, inputName=inputName,
                                      outputLayer=tf.keras.layers.Dense(outputDimension, activation=outputActivation, name=outputName),
                                      name=name, modelPath=modelPath)
     
        self.encodingLayers = 0
        
        self.addEncodingLayer(filters=12, index=-1)
        self.addLayer(tf.keras.layers.Flatten(), -1)

    
    def addEncodingLayer(self, layers=[], filters=24, kernel_size=3, strides=2, activation=tf.nn.relu, padding="same", index=-2) -> None:
        """
        Given a list of tensorflow layers those layers are added to the encoder.
        The default layer being a 2D convolutional layer to learn and downscale the image.
        Great image explanation here:
        https://miro.medium.com/max/3288/1*uAeANQIOQPqWZnnuH-VEyw.jpeg

        Args:
            layers (list, optional): The list of layers to add to the encoder as a encoding layer. Defaults to [].
            filters (int, optional): The filters for the 2D convolutional layer. Defaults to 24.
            kernel_size (int, optional): The kernel size for the 2D convolutional layer. Defaults to 3.
            strides (int, optional): The factor by which the x and y dimensions will be divided by for the 2D convolutional layer. Defaults to 2.
            activation (function, optional): The activation function for the 2D convolutional layer. Defaults to tf.nn.relu.
            padding (str, optional): The padding for the 2D convolutional layer. Defaults to "same".
            index (int, optional): The position to insert each layer within layers. Defaults to -2.

        Raises:
            LayerIndexOutOfRangeError: If the layer trying to be added is at an index not within the list.
        """

        if abs(index) > len(self.modelLayers) -1 or abs(index) < 1:
            raise LayerIndexOutOfRangeError(index, len(self.modelLayers) - 1)
            
        if index > 0:
            index = -(len(self.modelLayers)-index)
        
        if len(layers) == 0:
            self.addLayer(layer=tf.keras.layers.Conv2D(filters, kernel_size, strides, padding, activation=activation),
                          index=index)
        
        for layer in layers:
            self.addLayer(layer, index)

        self.encodingLayers += 1
