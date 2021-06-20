#pylint: disable=C0103, C0301
"""
The utility functions related to datasets
"""
__author__ = "Noupin"

#Third Party Imports
import numpy as np
import tensorflow as tf
from typing import Callable, List, Union
from tensorflow.python.data.ops import dataset_ops


def datasetFrom(data: Union[np.ndarray, List, Callable, tf.data.Dataset], bufferSize=None, batchSize=1, **kwargs) -> tf.data.Dataset:
    """
    Converts a list, numpy array, or generator to a TensorFlow dataset.

    Args:
        data (Union[np.ndarray, List, Callable]): The data to convert to a dataset.
        bufferSize (int, optional): The size of the buffer to select from for randomization. Defaults to None.
        batchSize (int, optional): The amount of data to include in each batch. Defaults to 1.
        kwargs: The keyword arguments to pass into the tf.data.Dataset.from_generator function.

    Returns:
        tf.data.Dataset: The created dataset.
    """

    if isinstance(data, tf.data.Dataset):
        if isinstance(data, dataset_ops.BatchDataset):
            return data
        dataset = data

    elif isinstance(data, np.ndarray) or isinstance(data, list):
        dataset = tf.data.Dataset.from_tensor_slices(data)

    elif callable(data):
        dataset = tf.data.Dataset.from_generator(data, **kwargs)

    else:
        raise TypeError(f"The type: {type(data)} cannot be converted to a TensorFlow dataset.")

    if not bufferSize:
        return dataset.batch(batchSize)

    return dataset.shuffle(bufferSize).batch(batchSize)
