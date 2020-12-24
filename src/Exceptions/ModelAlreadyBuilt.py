#pylint: disable=C0103, C0301, E1101
"""
Error for already built models in tensorflow
"""
__author__ = "Noupin"

#Third Party Imports
from colorama import Fore


class ModelAlreadyBuiltError(Exception):
    """
    Exception raised for errors of trying to build already built models.
    """

    def __init__(self, message="The model you are trying to build has already been built and cannot be built again."):
        self.message = message

        super().__init__(self.message)
    

    def __str__(self) -> str:
        return Fore.RED + f"{self.message}" + Fore.RESET