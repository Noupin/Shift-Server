#pylint: disable=C0103, C0301, R0903
"""
Base tensorflow model
"""
__author__ = "Noupin"

#Third Party Imports
import os
import gc
import sys
import time
import numpy as np
import tensorflow as tf
from colorama import Fore
from itertools import chain
from typing import List, Tuple, Union, Generator

#First Party Imports
from src.utils.image import viewImage
from src.utils.memory import allowTFMemoryGrowth
from src.Exceptions.ModelAlreadyBuilt import ModelAlreadyBuiltError
from src.Exceptions.IncompatibleTFLayers import IncompatibleTFLayerError
from src.Exceptions.LayerIndexOutOfRange import LayerIndexOutOfRangeError


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
                       loss=tf.losses.mean_squared_logarithmic_error, name="TFModel",
                       modelPath="modelPath"):

        allowTFMemoryGrowth()
        super(TFModel, self).__init__()

        self.loss = loss
        self.optimizer = optimizer

        self.modelLayers = []
        self.modelName = name
        self.modelBuilt = False
        self.modelLoaded = False

        self.modelLayers.append(inputLayer)
        self.modelLayers.append(outputLayer)

        self.model = None


    @tf.function
    def call(self, layer: tf.keras.layers.Layer) -> tf.keras.layers.Layer:
        """
        The method TensorFlow uses when calling the class as a tf.keras.Model

        Args:
            layer (tensorflow.python.framework.ops.Tensor): The starting layer of the model

        Raises:
            IncompatibleTFLayerError: One or more of the layers in self.modelLayers are incompatible

        Returns:
            tensorflow.python.framework.ops.Tensor: The last layer in the connected model
        """

        ###################################################################################################
        # Need to figure out how to call layers with weights or return loaded models as conencted tensors #
        ###################################################################################################
        connectedLayers = [layer]
        
        for modelLayer in range(1, len(self.modelLayers)):
            try:
                connectedLayers.append(self.modelLayers[modelLayer](connectedLayers[modelLayer-1]))
            except ValueError:
                raise IncompatibleTFLayerError(connectedLayers[modelLayer-1], self.modelLayers[modelLayer])

        return connectedLayers[-1]


    @tf.function
    def trainStep(self, x, y) -> tuple:
        """
        Inferences on the x data and applies a gradient using the loss when
        the inference is compared to the actual outputs y.

        Args:
            x : Data to inference on
            y : Data to compute the loss funciton with

        Returns:
            tuple: The loss vale for each value in the x data
        """

        with tf.GradientTape() as tape:
            logits = self(x, training=True)
            loss_value = self.loss(y, logits)

        grads = tape.gradient(loss_value, self.trainable_weights)
        self.optimizer.apply_gradients(zip(grads, self.trainable_weights))

        return loss_value
    

    @tf.function
    def testStep(self, x, y) -> None:
        """
        Inferences on the x data and finds the acuracy to update metrics if needed.

        Args:
            x : Data to inference on
            y : Data to compute the loss funciton with
        """

        val_logits = self(x, training=False)


    def train(self, xTrainData: Union[List[np.ndarray], Generator[None, np.ndarray, None]],
                    yTrainData: Union[List[np.ndarray], Generator[None, np.ndarray, None]]=None,
                    xTestData: Union[List[np.ndarray], Generator[None, np.ndarray, None]]=None,
                    yTestData: Union[List[np.ndarray], Generator[None, np.ndarray, None]]=None,
                    epochs: int=1, batch_size: int=1) -> None:

        """
        Trains the model given traingin data. This an an alternative to the .fit() with more customizability.

        Args:
            xTrainData (list of numpy.ndarray or Generator): The inputs for training the model.
            yTrainData (list of numpy.ndarray or Generator, optional): The expected outputs for training the model. Defaults to None.
            xTestData (list of numpy.ndarray or Generator, optional): The inputs for testing or validating the model. Defaults to None.
            yTestData (list of numpy.ndarray or Generator, optional): The expected outputs for testing or validating the model. Defaults to None.
            epochs (int, optional): The amount of iterations to train. Defaults to 1.
            batch_size (int, optional): Then size to batch the data into. Defaults to 1.
        """

        #self.fit(xTrainData, xTrainData, batch_size=batch_size, epochs=epochs)

        isGenerator = False

        if isinstance(xTrainData, Generator) and isinstance(yTrainData, Generator):
            trainDataset = ((x, y) for (x, y) in zip(xTrainData, yTrainData))
            isGenerator = True
        elif isinstance(xTrainData, Generator):
            trainDataset = ((x, y) for (x, y) in zip(xTrainData, xTrainData))
            isGenerator = True
        elif np.array(yTrainData).any():
            trainDataset = tf.data.Dataset.from_tensor_slices((xTrainData, yTrainData))
        else:
            trainDataset = tf.data.Dataset.from_tensor_slices((xTrainData, xTrainData))

        if not isGenerator:
            trainDataset = trainDataset.batch(batch_size)
        
        if np.array(xTestData).any() and np.array(yTestData).any():
            testDataset = tf.data.Dataset.from_tensor_slices(xTestData, yTestData)
        elif np.array(xTestData).any():
            testDataset = tf.data.Dataset.from_tensor_slices(xTestData, xTestData)
        else:
            testDataset = tf.data.Dataset.from_tensor_slices([])
        testDataset.batch(batch_size)


        for epoch in range(epochs):
            epochStart = time.time()
            reducedLoss = 0
            #Iterate over batches of dataset
            if isGenerator:
                currentData = 1
                step = 0
                while currentData:
                    batchStart = time.time()
                    xBatchTrain = []
                    yBatchTrain = []
                    for image in range(batch_size):
                        currentData = next(trainDataset, None)
                        if not currentData:
                            break

                        xData, yData = currentData
                        xBatchTrain.append(xData)
                        yBatchTrain.append(yData)
                    
                    xBatchTrain = np.array(xBatchTrain)
                    yBatchTrain = np.array(yBatchTrain)

                    loss_value = self.trainStep(xBatchTrain, yBatchTrain)
                    reducedLoss = tf.reduce_mean(tf.abs(loss_value))
                    print(f"Loss for batch {step+1}: {tf.reduce_mean(tf.abs(loss_value))}, Time: {time.time()-batchStart}")

                    step += 1

            else:
                for step, (xBatchTrain, yBatchTrain) in enumerate(trainDataset):
                    loss_value = self.trainStep(xBatchTrain, yBatchTrain)
                    reducedLoss = tf.reduce_mean(tf.abs(loss_value))
                    print(f"Loss for batch {step+1}: {reducedLoss}")
            
            for xBatchTest, yBatchTest in testDataset:
               self.testStep(xBatchTest, yBatchTest)

            
            print(f"Loss: {reducedLoss}, Time: {time.time()-epochStart}")
        
        #Clear dataset to perserve RAM
        trainDataset = tf.data.Dataset.from_tensor_slices([])


    def addLayer(self, layer: tf.keras.layers.Layer, index=-1) -> None:
        """
        Adds the given layer to self.modelLayers at index.

        Args:
            layer (tf.keras.layers.Layer): The layer to be added to self.model.
            index (int): The index at which to add layer. Defaults to -1.
        """

        if abs(index) > len(self.modelLayers):
            raise LayerIndexOutOfRangeError(index, len(self.modelLayers))

        self.modelLayers.insert(index, layer)


    def buildModel(self) -> None:
        """
        \t*Model can only be made once. Once the model is made no more layers can be added.*\n
        Creates a tensorflow model from the layers in self.modelLayers and assigns that model to self.model.

        Raises:
            IncompatibleTFLayerError: One or more of the layers in self.modelLayers are incompatible
        """

        if self.modelBuilt:
            raise ModelAlreadyBuiltError

        self.modelLayers = tuple(self.modelLayers)
        connectedLayers = [self.modelLayers[0]]
        
        for modelLayer in range(1, len(self.modelLayers)):
            try:
                connectedLayers.append(self.modelLayers[modelLayer](connectedLayers[modelLayer-1]))
            except ValueError:
                raise IncompatibleTFLayerError(connectedLayers[modelLayer-1], self.modelLayers[modelLayer])

        self.model = tf.keras.Model(inputs=connectedLayers[0], outputs=connectedLayers[-1], name=self.modelName)
        self.modelBuilt = True

        del connectedLayers


    def load(self, path: str) -> None:
        """
        Load the encoder given a filepath and a filename to load from.

        Args:
            path (str): Filepath to a tensorflow model to be loaded.
        """

        self.model = tf.keras.models.load_model(path)

        self.modelLoaded = True
        #self.modelBuilt = True


    def compileModel(self, optimizer: tf.optimizers.Optimizer=None, loss=None) -> None:
        """
        Compiles self.model.

        Args:
            optimizer (tf.optimizers.Optimizer, optional): The optimizer to apply to self.model. Defaults to None.
            loss (function, optional): The loss to apply to self.model. Defaults to None.
        """

        if optimizer:
            self.optimizer = optimizer
        if loss:
            self.loss = loss

        self.compile(optimizer=self.optimizer, loss=self.loss)
