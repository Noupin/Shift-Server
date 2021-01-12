#pylint: disable=C0103, C0301
"""
Reference variables with their getters and setters for the API
"""
__author__ = "Noupin"


class Globals:
    __trainVar = False
    __inferenceVar = False
    __progressVar = 0


    @property
    def training(self) -> bool:
        return self.__trainVar
    
    @training.setter
    def training(self, val: bool) -> None:
        if type(val) != bool:
            raise TypeError("Training value must be a boolean")

        self.__trainVar = val


    @property
    def inferencing(self) -> bool:
        return self.__inferenceVar
    
    @inferencing.setter
    def inferencing(self, val: bool) -> None:
        if type(val) != bool:
            raise TypeError("Inferencing value must be a boolean")

        self.__inferenceVar = val


    @property
    def progress(self) -> int:
        return self.__progressVar
    
    @progress.setter
    def progress(self, val: int) -> None:
        if val < 0 or val > 100:
            raise ValueError("Progress value must be between 0 and 100")

        self.__progressVar = val
        