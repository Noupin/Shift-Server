#pylint: disable=C0103, C0301, R0903
"""
The utility functions related to files
"""
__author__ = "Noupin"

#Third Party Imports
import os
import uuid
import base64
import werkzeug
from flask import current_app
from typing import Union, List
from werkzeug.utils import secure_filename

#First Party Imports
from src.variables.constants import EXTENSION_FILE_TYPES, SHIFT_PATH


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


def makeShiftFolders(folderPath: str) -> None:
    """
    Creates the folder for the shift models and the temporary data needed.

    Args:
        folderPath (str): The base of the folder path to make other folders
    """
    
    makeDir(folderPath)
    makeDir(os.path.join(folderPath, "tmp"))
    makeDir(os.path.join(folderPath, "tmp", "original"))
    makeDir(os.path.join(folderPath, "tmp", "base"))
    makeDir(os.path.join(folderPath, "tmp", "mask"))


def saveFlaskFile(data: werkzeug.datastructures.FileStorage, uuid: str, requestData: List[str], count=0) -> None:
    """
    Saves the data from a werkzeug file object to the file system

    Args:
        data (werkzeug.datastructures.FileStorage): The data to be saved to the file system.
        uuid (str): The uuid of the folder to save the files to.
        requestData (list of str): The additional data with the request needed for naming the file.
        count (int, optional): The counter to change the filename of the data
                               being saved. Defaults to 0.
    """

    filename = secure_filename(data.filename)
    folderPath = os.path.join(current_app.root_path, SHIFT_PATH, uuid)
    makeShiftFolders(folderPath)

    #FileStorage.save deletes the object
    if count == 0:
        data.save(os.path.join(folderPath, "tmp", "original", filename))
    elif requestData[count] == "base":
        data.save(os.path.join(folderPath, "tmp", "base", filename))
    elif requestData[count] == "mask":
        data.save(os.path.join(folderPath, "tmp", "mask", filename))
