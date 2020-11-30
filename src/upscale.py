#pylint: disable=C0103, C0301, R0903
"""
The custom upscaling network for Shift
"""
__author__ = "Noupin"

#Third Party Imports
import os
import tensorflow as tf

#First Party Imports
from tunable import Tunable
from constants import Constants


class Upscale:
    """
    The custom built upscale network for Shift
    """

    def __init__(self):
        #128x128 Input
        inputLayer = tf.keras.Input(shape=(Tunable.tunableDict["imgX"],
                                           Tunable.tunableDict["imgY"],
                                           Tunable.tunableDict["colorDim"]),
                                    name="Low-Res_Image")

        hiddenLayer = tf.keras.layers.Reshape((Tunable.tunableDict["imgX"],
                                               Tunable.tunableDict["imgY"],
                                               Tunable.tunableDict["colorDim"]))(inputLayer)

        #Upscale to 256x256
        '''for conv in range(convTimes):
            hiddenLayer = tf.keras.layers.Conv2D(convFilters*(2**conv),
                                                convFilterSize,
                                                activation=tf.nn.relu,
                                                padding="same")(hiddenLayer)'''
        hiddenLayer = tf.keras.layers.Conv2D(Tunable.tunableDict["convFilters"],
                                             Tunable.tunableDict["convFilterSize"],
                                             activation=tf.nn.relu,
                                             padding="same")(hiddenLayer)
        hiddenLayer = tf.keras.layers.UpSampling2D(Tunable.tunableDict["poolSize"])(hiddenLayer)

        #Upscale to 512x512
        hiddenLayer = tf.keras.layers.Conv2D(Tunable.tunableDict["convFilters"],
                                             Tunable.tunableDict["convFilterSize"],
                                             activation=tf.nn.relu,
                                             padding="same")(hiddenLayer)
        hiddenLayer = tf.keras.layers.UpSampling2D(Tunable.tunableDict["poolSize"])(hiddenLayer)

        #Upscale to 1024x1024
        hiddenLayer = tf.keras.layers.Conv2D(Tunable.tunableDict["convFilters"],
                                             Tunable.tunableDict["convFilterSize"],
                                             activation=tf.nn.relu,
                                             padding="same")(hiddenLayer)
        hiddenLayer = tf.keras.layers.UpSampling2D(Tunable.tunableDict["poolSize"])(hiddenLayer)

        #Resahpe to RGB color space
        outputLayer = tf.keras.layers.Conv2D(Tunable.tunableDict["colorDim"],
                                             Tunable.tunableDict["convFilterSize"],
                                             activation=tf.nn.relu,
                                             padding="same")(hiddenLayer)

        self.model = tf.keras.models.Model(inputLayer, outputLayer, name="Upscale")


        self.model.compile(optimizer=tf.optimizers.Adam(learning_rate=0.01),
                           loss=tf.losses.mean_squared_logarithmic_error)

    def train(self, x_train, x_test):
        """
        Train the upscale model given a train and test dataset
        """

        self.model.fit(x_train, x_test,
                       epochs=Tunable.tunableDict["epochs"],
                       batch_size=Tunable.tunableDict["batchSize"],
                       callbacks=[tf.keras.callbacks.ReduceLROnPlateau(monitor="loss",
                                                                       factor=0.1,
                                                                       patience=5)])

    def save(self, filename):
        """
        Saving the upscale model given a file name
        """

        self.model.save(os.path.join(Constants.defaultModelPath, "{}.upsc".format(filename)))

    def load(self, filename):
        """
        Load the upscale modle given a file name
        """

        self.model = tf.keras.models.load_model(os.path.join(Constants.defaultModelPath, "{}.upsc".format(filename)))
