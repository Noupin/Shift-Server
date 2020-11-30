#pylint: disable=C0103, C0301
"""
The custom decoder model for Shift
"""
__author__ = "Noupin"

#Third Party Imports
import tensorflow as tf

#First Party Imports
from tunable import Tunable


class AE:
    """
    The custom built decoder layer for Shift
    """

    def __init__(self, encoder, decoder):
        self.inputLayer = tf.keras.Input(shape=(Tunable.tunableDict["imgX"],
                                                Tunable.tunableDict["imgY"],
                                                Tunable.tunableDict["colorDim"]),
                                         name="Image")

        self.encodedImg = encoder(self.inputLayer)
        self.decodedImg = decoder(self.encodedImg)

        self.model = tf.keras.models.Model(self.inputLayer, self.decodedImg, name="AE")
        self.model.compile(optimizer=tf.optimizers.Adam(),
                           loss=tf.losses.mean_squared_logarithmic_error)

    def compile(self):
        """
        Recompile the autoencoder model
        """

        self.model.compile(optimizer=tf.optimizers.Adam(),
                           loss=tf.losses.mean_squared_logarithmic_error)
        print("Recompiled Model.")

    def train(self, x_train, x_test, epochs):
        """
        Given a number of epochs and a train and test dataset the model with be trained
        """

        self.model.fit(x_train, x_train,
                       epochs=epochs,
                       validation_data=(x_test, x_test),
                       batch_size=32)

    def predict(self, x_):
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
