#pylint: disable=C0103, C0301, R0903
"""
The custom Discriminator model for TFModel
"""
__author__ = "Noupin"

#Third Party Imports
import tensorflow as tf

#First Party Imports
from src.AI.TFModel import TFModel
from src.Exceptions.LayerIndexOutOfRange import LayerIndexOutOfRangeError


class Discriminator(TFModel):
    """
    A Base Encoder TensorFlow model for Feryv projects.

    Args:
        inputShape (tuple of int, optional): The input shape for the discriminator model. Defaults to (256, 256, 3).
        inputName (str, optional): The name of the input layer. Defaults to "InputImage".
        outputDimension (int, optional): The dimensionality of the latent space. Defaults to 512.
        outputName (str, optional): The name of the output layer. Defaults to "LatentOutput".
        outputActivation (function, optional): The activation function for the output layer. Defaults to tf.nn.relu.
        name (str, optional): The name for model. Defaults to "Discriminator".
    """

    def __init__(self, inputShape=(256, 256, 3), inputName="InputImage",
                 outputName="RealOrFake", outputActivation=tf.nn.relu, name="Discriminator",
                 optimizer: tf.keras.optimizers.Optimizer=tf.optimizers.Adam):
        super(Discriminator, self).__init__(inputShape=inputShape, inputName=inputName,
                                      outputLayer=tf.keras.layers.Dense(1, activation=outputActivation, name=outputName),
                                      name=name, optimizer=optimizer)
        
        self.addLayer(tf.keras.layers.Flatten(), -1)
        self.addDiscriminatorLayer()


    def addDiscriminatorLayer(self, filters=24, kernel_size=3, strides=2, activation=tf.nn.relu,
                              padding="same", index=-2, withDropout=True, dropoutRate=0.3):
        """
        Args:
            filters (int, optional): The filters for the 2D convolutional layer. Defaults to 24.
            kernel_size (int, optional): The kernel size for the 2D convolutional layer. Defaults to 3.
            strides (int, optional): The factor by which the x and y dimensions will be divided by for the 2D convolutional layer. Defaults to 2.
            activation (function, optional): The activation function for the 2D convolutional layer. Defaults to tf.nn.relu.
            padding (str, optional): The padding for the 2D convolutional layer. Defaults to "same".
            index (int, optional): The position to insert each layer within layers. Defaults to -2.
            withDropout (bool, optional): Whether or not too a dorpout layer aswell. Defaults to True.
            dropoutRate (float, optional): The rate for the dorpout layer. Defaults to 0.3.

        Raises:
            LayerIndexOutOfRangeError: If the layer trying to be added is at an index not within the list.
        """

        if abs(index) > len(self.modelLayers) -1 or abs(index) < 1:
            raise LayerIndexOutOfRangeError(index, len(self.modelLayers) - 1)
            
        if index > 0:
            index = -(len(self.modelLayers)-index)
        
        self.addLayer(layer=tf.keras.layers.Conv2D(filters, kernel_size, strides, padding, activation=activation),
                      index=index)
        if withDropout:
            self.addLayer(layer=tf.keras.layers.Dropout(dropoutRate), index=index)
