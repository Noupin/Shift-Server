#pylint: disable=C0103, C0301, R0903
"""
The custom decoder model for Shift
"""
__author__ = "Noupin"

#Third Party Imports
import os
import tensorflow as tf

#First Party Imports
from tunable import Tunable


class Decoder:
    """
    The custom built decoder layer for Shift
    """

    def __init__(self):
        self.inputLayer = tf.keras.Input(shape=(Tunable.tunableDict["latentSize"],), name="EncodedImage")
        self.hiddenLayer = tf.keras.layers.Dense((int(Tunable.tunableDict["imgX"]/(2**Tunable.tunableDict["convLayers"]))*
                                                  int(Tunable.tunableDict["imgY"]/(2**Tunable.tunableDict["convLayers"]))*
                                                  Tunable.tunableDict["convFilters"]),
                                                 activation=tf.nn.relu)(self.inputLayer)
        self.hiddenLayer = tf.keras.layers.Reshape((int(Tunable.tunableDict["imgX"]/(2**Tunable.tunableDict["convLayers"])),
                                                    int(Tunable.tunableDict["imgY"]/(2**Tunable.tunableDict["convLayers"])),
                                                    Tunable.tunableDict["convFilters"]))(self.hiddenLayer)

        self.hiddenLayer = tf.keras.layers.Conv2D(Tunable.tunableDict["convFilters"],
                                                  Tunable.tunableDict["convFilterSize"],
                                                  activation=tf.nn.relu,
                                                  padding="same")(self.hiddenLayer)
        self.hiddenLayer = tf.keras.layers.UpSampling2D(Tunable.tunableDict["poolSize"])(self.hiddenLayer)

        for layer in range(Tunable.tunableDict["convLayers"]-1):
            self.hiddenLayer = tf.keras.layers.Conv2D(Tunable.tunableDict["convFilters"], #*(2**(layer+1)),
                                                      Tunable.tunableDict["convFilterSize"],
                                                      activation=tf.nn.relu,
                                                      padding="same")(self.hiddenLayer)
            self.hiddenLayer = tf.keras.layers.UpSampling2D(Tunable.tunableDict["poolSize"])(self.hiddenLayer)

        self.outputLayer = tf.keras.layers.Conv2D(Tunable.tunableDict["colorDim"],
                                                  Tunable.tunableDict["convFilterSize"],
                                                  activation=tf.nn.relu,
                                                  padding="same")(self.hiddenLayer)
        self.model = tf.keras.models.Model(self.inputLayer, self.outputLayer, name="Decoder")
        self.model.compile(optimizer=tf.optimizers.Adam(), loss=tf.losses.mean_squared_logarithmic_error)

    def save(self, filepath, filename):
        """
        Save the decoder given a filepath and filename to save to
        """

        print("Saving Decoder.")
        self.model.save(os.path.join(filepath, "{}.dec".format(filename)))

    def load(self, filepath, filename):
        """
        Load the decoder given a filepath and a filename to load from
        """

        self.model = tf.keras.models.load_model(os.path.join(filepath, "{}.dec".format(filename)))
