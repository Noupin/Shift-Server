#pylint: disable=C0103, C0301, E1101
"""
Error for different image shapes when converting from list of images to video.
"""
__author__ = "Noupin"

#Third Party Imports
import numpy as np
from typing import Tuple
from colorama import Fore


class IncompatibleShapeError(Exception):
    """
    Exception raised for different image shapes when converting from list of images to video.
    """

    def __init__(self, imageShape: Tuple[int], videoShape: Tuple[int], message="Shapes are incompatible."):
        self.imageShape = imageShape
        self.videoShape = videoShape
        self.message = message

        super().__init__(self.message)
    

    def __str__(self) -> str:
        return Fore.RED + f"({self.imageShape}, {self.videoShape}) -> {self.message}" + Fore.RESET