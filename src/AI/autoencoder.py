#pylint: disable=C0103, C0301
"""
The custom Autoencoder model for TFModel
"""
__author__ = "Noupin"

#Third Party Imports
import tensorflow as tf

#First Party Imports
from src.AI.TFModel import TFModel
from src.AI.Encoder import Encoder
from src.AI.Decoder import Decoder


class Autoencoder(TFModel):
    """
    An Autoencoder TensorFlow model for Feryv projects.

    Args:
        inputShape (tuple, optional): The resolution and color channels for the input image. Defaults to (256, 256, 3).
        inputName (str, optional): The name of the input layer. Defaults to "InputImage".
        encoder (AI.encoder.Encoder, optional): The encoder. Defaults to Encoder().
        decoder (AI.encoder.Decoder, optional): The decoder. Defaults to Decoder().
        optimizer (tf.optimizers.Optimizer, optional): The optimizer to use when compiling the model. Defaults to tf.optimizers.Adam().
        loss (function, optional): The loss function to use when compiling the model. Defaults to tf.losses.mean_absolute_error.
    """

    def __init__(self, inputShape=(256, 256, 3), inputName="InputImage", encoder=Encoder(), decoder=Decoder(),
                       optimizer=tf.optimizers.Adam(), loss=tf.losses.mean_squared_logarithmic_error, name="Autoencoder",):
        super(Autoencoder, self).__init__(inputShape=inputShape, inputName=inputName,
                                          outputLayer=decoder,
                                          optimizer=optimizer, loss=loss,
                                          name=name)

        self.encoderLayer = encoder
        self.decoderLayer = decoder

        self.addLayer(self.encoderLayer)
