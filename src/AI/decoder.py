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
    A Base Decoder TensorFlow model for Vardia projects.

    Args:
        inputShape (tuple of int, optional): The latent space input shape for the decoder model. Defaults to (512,).
        inputName (str, optional): The name of the input layer. Defaults to "LatentInput".
        latentReshape (tuple of int, optional): The shape to convert the latent space to. Defaults to (128, 128, 3).
        outputDimension (int, optional): The dimensionality of the latent space. Defaults to 3.
        outputName (str, optional): The name of the output layer. Defaults to "OutputImage".
        outputActivation (function, optional): The activation function for the output layer. Defaults to tf.nn.relu.
        name (str, optional): The name for model. Defaults to "Decoder".
    """

    def __init__(self, inputShape=(512,), inputName="LatentInput",
                       latentReshape=(128, 128, 24),
                       outputDimension=3, outputName="OutputImage", outputActivation=tf.nn.relu,
                       name="Decoder"):
        super(Decoder, self).__init__(inputLayer=tf.keras.Input(shape=inputShape, name=inputName),
                                      outputLayer=tf.keras.layers.Conv2DTranspose(filters=outputDimension, kernel_size=3, strides=1,
                                                                         padding="same", activation=outputActivation, name=outputName),
                                      name=name)
     
        self.decodingLayers = 0
        
        self.addLayer(tf.keras.layers.Dense(prod(latentReshape), activation=outputActivation), 1)
        self.addLayer(tf.keras.layers.Reshape(target_shape=latentReshape), -1)
        self.addDecodingLayer(filters=12, index=-1)


    def addDecodingLayer(self, layers=[], filters=24, kernel_size=3, strides=2, activation=tf.nn.relu, padding="same", index=-2):
        """
        Given a list of tensorflow layers those layers are added to the decoder.
        The default layer being a 2D convolutional transposing layer to learn and upscale the image.
        Great image explanation here:
        https://miro.medium.com/max/3288/1*uAeANQIOQPqWZnnuH-VEyw.jpeg

        Args:
            layers (list, optional): The list of layers to add to the decoder as a decoding layer. Defaults to [].
            filters (int, optional): The filters for the 2D convolutional transposing layer. Defaults to 24.
            kernel_size (int, optional): The kernel size for the 2D convolutional transposing layer. Defaults to 3.
            strides (int, optional): The factor by which the x and y dimensions will be multiplied by for the 2D convolutional transposing layer. Defaults to 2.
            activation (function, optional): The activation function for the 2D convolutional transposing layer. Defaults to tf.nn.relu.
            padding (str, optional): The padding for the 2D convolutional transposing layer. Defaults to "same".
            index (int, optional): The position to insert each layer within layers. Defaults to -2.

        Raises:
            LayerIndexOutOfRangeError: If the layer trying to be added is at an index not within the list.
        """

        if abs(index) > len(self.modelLayers) -1 or abs(index) < 1:
            raise LayerIndexOutOfRangeError(index, len(self.modelLayers) - 1)
            
        if index > 0:
            index = -(len(self.modelLayers)-index)
        
        if len(layers) == 0:
            self.addLayer(tf.keras.layers.Conv2DTranspose(filters, kernel_size, strides, padding, activation=activation), index)

        for layer in layers:
            self.addLayer(layer, index)

        self.decodingLayers += 1
