#pylint: disable=C0103, C0301, E1101
"""
The utility functions related to detection
"""
__author__ = "Noupin"

#Third Party Import
import sys
import subprocess
import tensorflow as tf
from typing import List
from collections import Mapping, Container


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
    except RuntimeError as error:
        print(error)


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


def chunkIterable(lst, n):
    """Yield successive n-sized chunks from lst."""

    for i in range(0, len(lst), n):
        yield lst[i:i + n]
    

def deep_getsizeof(o, ids):
    """Find the memory footprint of a Python object
 
    This is a recursive function that drills down a Python object graph
    like a dictionary holding nested dictionaries with lists of lists
    and tuples and sets.
 
    The sys.getsizeof function does a shallow size of only. It counts each
    object inside a container as pointer only regardless of how big it
    really is.
 
    :param o: the object
    :param ids:
    :return:
    """

    d = deep_getsizeof
    if id(o) in ids:
        return 0
 
    r = sys.getsizeof(o)
    ids.add(id(o))
 
    if isinstance(o, bytes) or isinstance(0, str):
        return r
 
    if isinstance(o, Mapping):
        return r + sum(d(k, ids) + d(v, ids) for k, v in o.iteritems())
 
    if isinstance(o, Container):
        return r + sum(d(x, ids) for x in o)
 
    return r 
