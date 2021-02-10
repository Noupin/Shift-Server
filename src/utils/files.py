#pylint: disable=C0103, C0301, R0903
"""
The utility functions related to files
"""
__author__ = "Noupin"

#Third Party Imports
import os
import uuid
import base64
from typing import Union

#First Party Imports
from src.variables.constants import EXTENSION_FILE_TYPES


def generateUniqueFilename(generator=uuid.uuid4, urlSafe=False) -> Union[uuid.UUID, str]:
    """
    Generates a unique filename.

    Args:
        generator (function): The function to use for the unique generation.
        urlSafe (bool): Whether the filename needs to be url safe or not. Defaults to False.

    Returns:
        uuid.UUID: The uniquley generated filename.
        str: The uniquely generated filename in string format.
    """

    uuid_ = generator()
    finalUUID = (uuid_, str(base64.urlsafe_b64encode(uuid_.bytes)).replace('=', '')[2:-1])[urlSafe]

    return finalUUID, str(finalUUID)


def checkPathExists(folderPath: str) -> bool:
    """
    Checks if the given folder path exists.

    Args:
        folderPath (str): The path and name of the folder to check if its exists
    
    Returns:
        bool: Whether the path exists or not
    """

    splitPath = os.path.split(folderPath)
    prevPath = splitPath[:-1]

    if prevPath == ('',):
        dirFiles = os.listdir()
    else:
        dirFiles = os.listdir(os.path.join(*prevPath))
    
    return splitPath[-1] in dirFiles


def makeDir(folderPath: str) -> bool:
    """
    Makes a directory given a path to the folder to make

    Args:
        folderPath (str): The path and name of the folder to make

    Returns:
        bool: Whether or not the folder was made
    """

    if checkPathExists(folderPath):
        return False
    
    os.mkdir(folderPath)

    return True


def getMediaType(filePath: str) -> str:
    """
    Given a path to a media file the type of the file will be returned. Ex. ('video', 'audio', 'image')

    Args:
        filePath (str): The path to the media file

    Returns:
        str: The type of the file
    """

    _, extension = os.path.splitext(filePath)

    return EXTENSION_FILE_TYPES[extension.lower()[1:]]
