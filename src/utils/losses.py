#pylint: disable=C0103, C0301, E1101
"""
The utility functions related to images
"""
__author__ = "Noupin"

#Third Party Imports
import tensorflow as tf
from tensorflow.keras import backend as K


def bernoulliLoss(y_true: tf.Tensor, y_pred: tf.Tensor) -> tf.Tensor:

    loss = (1/2)*K.sum((y_true-y_pred)**2, axis=1)

    return loss