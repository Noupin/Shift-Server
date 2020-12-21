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
    The custom built decoder layer for Shift
    """

    def __init__(self, inputShape=(256, 256, 3), inputName="InputImage", encoder=Encoder(), decoder=Decoder()):
        super(AutoEncoder, self).__init__(inputLayer=tf.keras.Input(shape=inputShape, name=inputName),
                                          outputLayer=decoder,
                                          name="AutoEncoder")

        self.inputLayer = tf.keras.Input(shape=inputShape, name=inputName)
        self.encoderLayer = encoder
        self.decoderLayer = decoder

        self.addLayer(self.encoderLayer)


    def train(self, x_train, x_test, epochs):
        """
        Given a number of epochs and a train and test dataset the model with be trained
        """

        self.model.fit(x_train, x_train,
                       epochs=epochs,
                       validation_data=(x_test, x_test),
                       batch_size=32)

    def pred(self, x_):
        """
        Given a certain input image and a model the model
        will inference and return an int array
        """

        output_img = self.model.predict(x_.reshape(1,
                                                   Tunable.tunableDict["imgX"],
                                                   Tunable.tunableDict["imgY"],
                                                   Tunable.tunableDict["colorDim"]))
        output_img = output_img[0].reshape(Tunable.tunableDict["imgX"],
                                           Tunable.tunableDict["imgY"],
                                           Tunable.tunableDict["colorDim"])

        return output_img #Base 1 img needs to be 255 and uint
