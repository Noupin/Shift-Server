#pylint: disable=C0103, C0301
"""
Reference variables with their getters and setters for the API
"""
__author__ = "Noupin"

#Third Party Imports
import werkzeug


class Globals:
    __trainVar = False
    __trainingUpdate = False
    __inferenceVar = False
    __progressVar = 0
    __currentJob = None
    __exhibitImages = []
    __files = None


    @property
    def training(self) -> bool:
        return self.__trainVar
    
    @training.setter
    def training(self, val: bool) -> None:
        if type(val) != bool:
            raise TypeError("Training value must be a boolean")

        self.__trainVar = val
    

    @property
    def trainingUpdate(self) -> bool:
        return self.__trainingUpdate
    
    @trainingUpdate.setter
    def trainingUpdate(self, val: bool) -> None:
        if type(val) != bool:
            raise TypeError("Training Update value must be a boolean")

        self.__trainingUpdate = val


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
    

    @property
    def job(self):
        return self.__currentJob
    
    @job.setter
    def job(self, val) -> None:
        self.__currentJob = val
    

    @property
    def exhibitImages(self):
        return self.__exhibitImages
    
    @exhibitImages.setter
    def exhibitImages(self, val) -> None:
        if not type(val) == list or not all(isinstance(n, str) for n in list):
            raise ValueError("Each element of the array must be an encoded image")

        self.__exhibitImages = val
    

    @property
    def files(self) -> werkzeug.datastructures.ImmutableMultiDict:
        return self.__files
    
    @files.setter
    def files(self, val) -> None:
        print(type(val))
        if not type(val) == werkzeug.datastructures.ImmutableMultiDict:
            raise ValueError("The value must be an Immutable Werkzeug MuliDict")

        self.__files = val
        