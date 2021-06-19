#pylint: disable=C0103, C0301, R0903
"""
Base TensorFlow model for TFModel
"""
__author__ = "Noupin"

#Third Party Imports
import time
import numpy as np
import tensorflow as tf
from typing import List, Tuple, Union, Generator

#First Party Imports
from src.utils.memory import allowTFMemoryGrowth
from src.Exceptions.IncompatibleShapes import IncompatibleShapeError
from src.Exceptions.IncompatibleTFLayers import IncompatibleTFLayerError
from src.Exceptions.LayerIndexOutOfRange import LayerIndexOutOfRangeError


class TFModel(tf.keras.Model):
    """
    A Base TensorFlow model for Feryv projects.

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

    def __init__(self, inputShape: Tuple[int]=(128, 128, 3), inputName: str="Input",
                       outputLayer: tf.keras.layers.Layer=tf.keras.layers.Dense(10, activation=tf.nn.relu, name="Output"),
                       activation=tf.nn.relu, optimizer: tf.keras.optimizers.Optimizer=tf.optimizers.Adam(),
                       loss=tf.losses.mean_squared_logarithmic_error, name: str="TFModel",
                       modelPath: str="modelPath"):

        allowTFMemoryGrowth()
        super(TFModel, self).__init__()

        self.loss = loss
        self.optimizer = optimizer
        self.inputShape = inputShape

        self.modelLayers: Union[List[tf.keras.layers.Layer], Tuple[tf.keras.layers.Layer]] = []
        self.modelName = name

        self.modelLayers.append(tf.keras.Input(inputShape, name=inputName))
        self.modelLayers.append(outputLayer)


    def call(self, tensor: Union[tf.Tensor, np.ndarray]) -> tf.Tensor:
        """
        The method TensorFlow uses when calling the class as a tf.keras.Model

        Args:
            tensor (tf.Tensor): The input to the model.

        Raises:
            IncompatibleTFLayerError: One or more of the layers in self.modelLayers are incompatible

        Returns:
            tf.Tensor: The last layer in the connected model
        """
        
        if not isinstance(self.modelLayers, tuple):
            self.modelLayers = tuple(self.modelLayers)

        connectedLayers = [tensor]

        for modelLayer in range(1, len(self.modelLayers)):
            try:
                connectedLayers.append(self.modelLayers[modelLayer](connectedLayers[modelLayer-1]))
            except ValueError as error:
                if modelLayer == 1:
                    raise ValueError(f"{str(error)}\nThe tensor being passed in to the model and the input layer of the model have incompatible shapes.")
                raise IncompatibleTFLayerError(connectedLayers[modelLayer-1], self.modelLayers[modelLayer], originalError=str(error))

        return connectedLayers[-1]


    def inference(self, tensor: tf.Tensor, asNumpy=True) -> Union[tf.Tensor, np.ndarray]:
        """
        The method TensorFlow uses when calling the class as a tf.keras.Model

        Args:
            tensor (tf.Tensor): The the tensor to inference with.
            asNumpy

        Returns:
            tf.Tensor or np.ndarray: The inferenced output.
        """

        if asNumpy:
            return self.call(tensor).numpy()
        else:
            return self.call(tensor)


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


    def train(self, xTrainData: Union[List[np.ndarray], Generator[np.ndarray, None, None]],
                    yTrainData: Union[List[np.ndarray], Generator[np.ndarray, None, None]]=None,
                    xTestData: Union[List[np.ndarray], Generator[np.ndarray, None, None]]=None,
                    yTestData: Union[List[np.ndarray], Generator[np.ndarray, None, None]]=None,
                    epochs: int=1, batch_size: int=1) -> None:

        """
        Trains the model given traingin data. This an an alternative to the .fit() with more customizability.

        Args:
            xTrainData (list of np.ndarray or Generator of np.ndarray): The inputs for training the model.
            yTrainData (list of np.ndarray or Generator of np.ndarray, optional): The expected outputs for training the model. Defaults to None.
            xTestData (list of np.ndarray or Generator of np.ndarray, optional): The inputs for testing or validating the model. Defaults to None.
            yTestData (list of np.ndarray or Generator of np.ndarray, optional): The expected outputs for testing or validating the model. Defaults to None.
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


        for _ in range(epochs):
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
                    print(f"Loss for batch {step+1}: {reducedLoss}, Time: {time.time()-batchStart}")

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
        
        if not isinstance(self.modelLayers, list):
            self.modelLayers = list(self.modelLayers)

        if abs(index) > len(self.modelLayers):
            raise LayerIndexOutOfRangeError(index, len(self.modelLayers))

        self.modelLayers.insert(index, layer)
    
    
    def saveModel(self, path: str):
        """
        Saves the given model to the path.

        Args:
            path (str): The path to save the model to.
        """

        #self.save_weights(path)
        self.save(path)


    def loadModel(self, path: str, compile=True, hasInputLayer=False, inputShape=None) -> None:
        """
        Load the model given a filepath and a filename to load from.

        Args:
            path (str): Filepath to a tensorflow model to be loaded.
            compile (bool, optional): Whether or not to compile the newly \
                loaded model. Defaults to True.
            hasInputLayer (bool, optional): Whether the model to be loaded has \
                an InputLayer. Defaults to False.
            inputShape (tuple of int, optional): The input shape of the model.
        """
        
        if not isinstance(self.modelLayers, tuple):
            self.modelLayers = tuple(self.modelLayers)
        
        if inputShape:
            self.inputShape = inputShape

        testTensor = np.zeros(self.inputShape, dtype=np.float32).reshape(1, *self.inputShape)

        loadedModel: tf.keras.Model = tf.keras.models.load_model(path)

        if not hasInputLayer:
            self.modelLayers = [tf.keras.Input(self.inputShape)]
            self.modelLayers += loadedModel.layers
            self.modelLayers = tuple(self.modelLayers)

        self.call(testTensor)
        self.set_weights(loadedModel.get_weights())
        
        if compile:
            self.compileModel()


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
