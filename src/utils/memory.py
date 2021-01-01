#pylint: disable=C0103, C0301, E1101
"""
The utility functions related to detection
"""
__author__ = "Noupin"

#Third Party Import
import os
import sys
import subprocess
import tensorflow as tf
from typing import List


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


def getGPUMemory() -> List[int]:
    """
    Gets the unused VRAM of each graphics card on the system.

    Returns:
        list of int: A list of unused VRAM for each card.
    """

    _output_to_list = lambda x: x.decode('ascii').split('\n')[:-1]

    ACCEPTABLE_AVAILABLE_MEMORY = 1024
    COMMAND = "nvidia-smi --query-gpu=memory.free --format=csv"
    memory_free_info = _output_to_list(subprocess.check_output(COMMAND.split()))[1:]
    memory_free_values = [int(x.split()[0]) for i, x in enumerate(memory_free_info)]

    return memory_free_values * 1_000_000


def getAmountForBuffer(data, bufferSize: int) -> int:
    """
    Gets the amount of items that can be stored in bufferSize.

    Args:
        data (any): The data to calculate how many items can fit in the given buffersize
        bufferSize (int): The buffer size to cotnrict the amount of data

    Returns:
        int: The number of items that can be stored in bufferSize
    """

    return int(bufferSize/sys.getsizeof(data))
