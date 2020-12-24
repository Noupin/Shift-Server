#pylint: disable=C0103, C0301, E1101
"""
The utility functions related to detection
"""
__author__ = "Noupin"

#Third Party Import
import tensorflow as tf


def allowTFMemoryGrowth() -> None:
    """
    Allows the memory to be allocated for tensorflow GPU and cudNN
    """

    gpus = tf.config.experimental.list_physical_devices('GPU')
    if not gpus:
        return

    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
    except RuntimeError as e:
        print(e)
