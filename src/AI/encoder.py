#pylint: disable=C0103, C0301, R0903
"""
The custom encoder model for Shift
"""
__author__ = "Noupin"

#Third Party Imports
import os
import tensorflow as tf

#First Party Imports
from tunable import Tunable


class Encoder:
    """
    The custom built encoder layer for Shift
    """

    def __init__(self):
        self.inputLayer = tf.keras.Input(shape=(Tunable.tunableDict["imgX"],
                                                Tunable.tunableDict["imgY"],
                                                Tunable.tunableDict["colorDim"]),
                                         name="Image")

        self.hiddenLayer = tf.keras.layers.Reshape((Tunable.tunableDict["imgX"],
                                                    Tunable.tunableDict["imgY"],
                                                    Tunable.tunableDict["colorDim"]),
                                                   input_shape=(Tunable.tunableDict["imgX"],
                                                                Tunable.tunableDict["imgY"],
                                                                Tunable.tunableDict["colorDim"]))(self.inputLayer)
        self.hiddenLayer = tf.keras.layers.Conv2D(Tunable.tunableDict["convFilters"],
                                                  Tunable.tunableDict["convFilterSize"],
                                                  activation=tf.nn.relu,
                                                  padding="same")(self.hiddenLayer)
        self.hiddenLayer = tf.keras.layers.MaxPooling2D(Tunable.tunableDict["poolSize"])(self.hiddenLayer)

        for layer in range(Tunable.tunableDict["convLayers"]-1):
            self.hiddenLayer = tf.keras.layers.Conv2D(Tunable.tunableDict["convFilters"], #*(2**(layer+1)),
                                                      Tunable.tunableDict["convFilterSize"],
                                                      activation=tf.nn.relu,
                                                      padding="same")(self.hiddenLayer)
            self.hiddenLayer = tf.keras.layers.MaxPooling2D(Tunable.tunableDict["poolSize"])(self.hiddenLayer)

        self.hiddenLayer = tf.keras.layers.Flatten()(self.hiddenLayer)
        self.outputLayer = tf.keras.layers.Dense(Tunable.tunableDict["latentSize"],
                                                 activation=tf.nn.relu)(self.hiddenLayer)

        self.model = tf.keras.models.Model(self.inputLayer, self.outputLayer, name="Encoder")
        self.model.compile(optimizer=tf.optimizers.Adam(), loss=tf.losses.mean_squared_logarithmic_error)

    def save(self, filepath, filename):
        """
        Save the encoder given a filepath and filename to save to
        """

        print("Saving Encoder.")
        self.model.save(os.path.join(filepath, "{}.enc".format(filename)))

    def load(self, filepath, filename):
        """
        Load the encoder given a filepath and a filename to load from
        """

        self.model = tf.keras.models.load_model(os.path.join(filepath, "{}.enc".format(filename)))
