#pylint: disable=C0103, C0301, E1101
"""
Error for converting from CV to PIL
"""
__author__ = "Noupin"

#Third Party Imports
import numpy as np
from colorama import Fore


class CVToPILError(Exception):
    """
    Exception raised for errors of CV to PIL image conversion.
    """

    def __init__(self, image: np.ndarray, message="Image already in CV form cannot convert."):
        self.type = type(image)
        self.message = message

        super().__init__(self.message)
    

    def __str__(self) -> str:
        return Fore.RED + f"{self.type} -> {self.message}" + Fore.RESET
