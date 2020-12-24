#pylint: disable=C0103, C0301, R0903
"""
Base tensorflow model
"""
__author__ = "Noupin"

#Third Party Imports
import os
import tensorflow as tf
from colorama import Fore

#First Party Imports
from utils.memory import allowTFMemoryGrowth
from Exceptions.IncompatibleTFLayers import IncompatibleTFLayerError
from Exceptions.LayerIndexOutOfRange import LayerIndexOutOfRangeError


class TFModel(tf.keras.Model):
    """
    A Base TensorFlow model for Vardia projects.

    Args:
        inputLayer (tf.keras.layers.Layer, optional): The input layer of the model. Defaults to
                                                      tf.keras.Input(shape=(128, 128, 3), name="Input").
        outputLayer (tf.keras.layers.Layer, optional): The output layer of the model. Defaults to
                                                       tf.keras.layers.Dense(10, activation=tf.nn.relu, name="Output").
        activation (function, optional): The default activaiton function for each layer of the model.
                                         Defaults to tf.nn.relu.
        optimizer (tf.optimizers.Optimizer, optional): The optimizer when compiling the model.
                                                       Defaults to tf.optimizers.Adam().
        loss (function, optional): The loss function when compliling the model.
                                   Defaults to tf.losses.mean_squared_logarithmic_error.
        name (str, optional): The name of the model. Defaults to "TFModel".
    """

    def __init__(self, inputLayer=tf.keras.Input(shape=(128, 128, 3), name="Input"),
                       outputLayer=tf.keras.layers.Dense(10, activation=tf.nn.relu, name="Output"),
                       activation=tf.nn.relu, optimizer=tf.optimizers.Adam(),
                       loss=tf.losses.mean_squared_logarithmic_error, name="TFModel"):
        allowTFMemoryGrowth()
        super(TFModel, self).__init__()

        self.loss = loss
        self.optimizer = optimizer

        self.modelLayers = []
        self.modelName = name
        self.modelBuilt = False

        self.modelLayers.append(inputLayer)
        self.modelLayers.append(outputLayer)

        self.model = tf.keras.Sequential()
    

    def call(self, layer):
        """
        The method TensorFlow uses when calling the class as a tf.keras.Model

        Args:
            layer (tensorflow.python.framework.ops.Tensor): The starting layer of the model

        Raises:
            IncompatibleTFLayerError: One or more of the layers in self.modelLayers are incompatible

        Returns:
            tensorflow.python.framework.ops.Tensor: The last layer in the connected model
        """

        connectedLayers = [layer]
        
        for modelLayer in range(1, len(self.modelLayers)):
            try:
                connectedLayers.append(self.modelLayers[modelLayer](connectedLayers[modelLayer-1]))
            except ValueError:
                raise IncompatibleTFLayerError(connectedLayers[modelLayer-1], self.modelLayers[modelLayer])

        return connectedLayers[-1]
    

    def addLayer(self, layer, index=-1):
        """
        Adds the given layer to self.modelLayers at index.

        Args:
            layer (tf.keras.layers.Layer): The layer to be added to self.model.
            index (int): The index at which to add layer. Defaults to -1.
        """

        if abs(index) > len(self.modelLayers):
            raise LayerIndexOutOfRangeError(index, len(self.modelLayers))

        self.modelLayers.insert(index, layer)
    

    def buildModel(self):
        """
        \t*Model can only be made once. Once the model is made no more layers can be added.*\n
        Creates a tensorflow model from the layers in self.modelLayers and assigns that model to self.model.

        Raises:
            IncompatibleTFLayerError: One or more of the layers in self.modelLayers are incompatible
        """

        if self.modelBuilt:
            print("Model already built this needs to be an error!")

        connectedLayers = [self.modelLayers[0]]
        
        for modelLayer in range(1, len(self.modelLayers)):
            try:
                connectedLayers.append(self.modelLayers[modelLayer](connectedLayers[modelLayer-1]))
            except ValueError:
                raise IncompatibleTFLayerError(connectedLayers[modelLayer-1], self.modelLayers[modelLayer])

        self.model = tf.keras.Model(inputs=connectedLayers[0], outputs=connectedLayers[-1], name=self.modelName)
        self.modelBuilt = True

        del connectedLayers


    def load(self, path):
        """
        Load the encoder given a filepath and a filename to load from.

        Args:
            path (str): Filepath to a tensorflow model to be loaded.
        """

        self.model = tf.keras.models.load_model(path)
    

    def compileModel(self, optimizer=None, loss=None):
        """
        Compiles self.model.

        Args:
            optimizer (tensorflow.python.keras.optimizer_v2, optional): The optimizer to apply to self.model. Defaults to None.
            loss (function, optional): The loss to apply to self.model. Defaults to None.
        """

        if optimizer:
            self.optimizer = optimizer
        if loss:
            self.loss = loss

        self.compile(optimizer=self.optimizer, loss=self.loss)
