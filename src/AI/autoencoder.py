#pylint: disable=C0103, C0301
"""
The custom decoder model for Shift
"""
__author__ = "Noupin"

#Third Party Imports
import tensorflow as tf

#First Party Imports
from AI.TFModel import TFModel
from AI.encoder import Encoder
from AI.decoder import Decoder


class AutoEncoder(TFModel):
    """
    An AutoEncoder TensorFlow model for Vardia projects.
    """

    def __init__(self, inputShape=(256, 256, 3), inputName="InputImage", encoder=Encoder(), decoder=Decoder(),
                       optimizer=tf.optimizers.Adam(), loss=tf.losses.mean_squared_logarithmic_error):
        super(AutoEncoder, self).__init__(inputLayer=tf.keras.Input(shape=inputShape, name=inputName),
                                          outputLayer=decoder,
                                          optimizer=optimizer, loss=loss,
                                          name="AutoEncoder")

        self.inputLayer = tf.keras.Input(shape=inputShape, name=inputName)
        self.encoderLayer = encoder
        self.decoderLayer = decoder

        self.addLayer(self.encoderLayer)
