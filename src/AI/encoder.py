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
    A Base Encoder TensorFlow model for Vardia projects.

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
                       name="Encoder"):
        super(Encoder, self).__init__(inputLayer=tf.keras.Input(shape=inputShape, name=inputName),
                                      outputLayer=tf.keras.layers.Dense(outputDimension, activation=tf.nn.relu, name=outputName),
                                      name=name)
     
        self.encodingLayers = 0
        
        #self.addLayer(tf.keras.layers.Reshape(inputShape), 1)
        self.addEncodingLayer(filters=12, index=-1)
        self.addLayer(tf.keras.layers.Flatten(), -1)

    
    def addEncodingLayer(self, layers=[], filters=24, kernel_size=3, strides=2, activation=tf.nn.relu, padding="same", index=-2):
        """
        Given a list of tensorflow layers those layers are added to the decoder.
        The default layers being a 2D convolutional layer and 2D max pooling layer
        to learn and downscale the image respectivley.
        Great image explanation here:
        https://miro.medium.com/max/3288/1*uAeANQIOQPqWZnnuH-VEyw.jpeg

        Args:
            layers (list of tf.keras.layers.Layer, optional): The list of layers to add to the decoder as a decoding layer.
                                       Defaults to [tf.keras.layers.Conv2D(5, (3, 3)), activation=tf.nn.relu, padding="same"),
                                       tf.keras.layers.MaxPooling2D((2,2)))]
            index (int, optional): The position to insert each layer within layers. Defaults to -1.
        """

        if abs(index) > len(self.modelLayers) -1 or abs(index) < 1:
            raise LayerIndexOutOfRangeError(index, len(self.modelLayers) - 1)
            
        if index > 0:
            index = -(len(self.modelLayers)-index)
        
        if len(layers) == 0:
            self.addLayer(tf.keras.layers.Conv2D(filters, kernel_size, strides, padding, activation=activation), index)
        
        for layer in layers:
            self.addLayer(layer, index)

        self.encodingLayers += 1
