#pylint: disable=C0103, C0301, E1101
"""
Error for incompatible tensorflow layers
"""
__author__ = "Noupin"

#Third Party Imports
from colorama import Fore


class LayerIndexOutOfRangeError(Exception):
    """
    Exception raised for errors of inserting a layer at an index greater than the amount of current layers.
    """

    def __init__(self, index, maxIndex, message="The index you are trying to insert the layer into is out of range of the current layers."):
        self.index = index
        self.maxIndex = maxIndex
        self.message = message

        super().__init__(self.message)
    

    def __str__(self):
        return Fore.RED + f"Index Out Of Range: {self.index} Max Index: {self.maxIndex} -> {self.message}" + Fore.RESET