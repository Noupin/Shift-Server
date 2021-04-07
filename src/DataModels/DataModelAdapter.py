#pylint: disable=C0103, C0301
"""
The MongoDB data model for a Train Worker
"""
__author__ = "Noupin"

#Third Party Imports
from typing import TypeVar, Generic


T = TypeVar('T')

class DataModelAdapter:
    """
    Adapting layer for non serializable data

    Args:
        DataModel (object): The data model object to be serialized
    """

    def __init__(self, DataModel: T):
        self.model = DataModel

    def getSerializable(self) -> dict:
        """
        Gets the the serializable version of self.model

        Returns:
            dict: The serializable version of self.model
        """

        return self.model.__dict__
    
    def getModel(self) -> T:
        """
        Gets the data model passed into the constructor

        Returns:
            T: The data model passed into the constructor
        """

        return self.model
