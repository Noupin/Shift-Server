#pylint: disable=C0103, C0301, E1101
"""
Error for incompatible tensorflow layers
"""
__author__ = "Noupin"

#Third Party Imports
import tensorflow as tf
from colorama import Fore


class IncompatibleTFLayerError(Exception):
    """
    Exception raised for errors of incompatible tensorflow layer combination.
    """

    def __init__(self, prevLayer: tf.keras.layers.Layer, nextLayer: tf.keras.layers.Layer, originalError: Exception, message="Layers are incompatible and cannot be combined."):
        self.prevLayer = prevLayer
        self.nextLayer = nextLayer
        self.message = message
        self.originalError = originalError

        super().__init__(self.message)
    

    def __str__(self) -> str:
        return Fore.RED + f"\nPrevious Layer: {self.prevLayer}\nNext Layer: \
{self.nextLayer}\nIncompatibilityError -> {self.message}\n\nOriginal \
Error: {self.originalError}" + Fore.RESET