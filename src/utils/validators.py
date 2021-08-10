#pylint: disable=C0103, C0301
"""
API Validators
"""
__author__ = "Noupin"

#Third Party Imports
import os
import re
from flask import current_app
from typing import List, Union, Tuple
from werkzeug.datastructures import FileStorage

#First Party Imports
from src.AI.Shift import Shift
from src.models.Request.TrainRequest import TrainRequest
from src.models.Request.InferenceRequest import InferenceRequest
from src.constants import (ALLOWED_EXTENSIONS, ALLOWED_SHIFT_TITLE_CHARACTERS, SHIFT_PATH,
                           ALLOWED_SHIFT_TITLE_SPECIAL_CHARACTERS, MAXIMUM_SHIFT_TITLE_LENGTH,
                           MINIMUM_SHIFT_TITLE_LENGTH)


def validateFilename(filename: str) -> bool:
    """
    Given a filename it returns a boolean whether the file is allowed

    Args:
        filename (str): The filename to be checked

    Returns:
        bool: Whether or not the file is valid by the filename
    """

    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def validateFileRequest(fileDict: List[FileStorage], fileIndicator="file") -> bool:
    """
    Given a dictionary of files from a flask request this will valiadate
    whether they are correctly keyed in the dicitonary.

    Args:
        fileDict (werkzeug.datastructures.MultiDict): The flask file request
        fileIndicator (str, optional): The string to search for in the dictionary
                                       keys to validate. Defaults to "file".

    Returns:
        bool: Whether the request is valid or not
    """

    valid = True

    if not fileDict:
        return False

    for currentFile in fileDict:
        if isinstance(currentFile, FileStorage):
            continue

        valid = False
        break
    
    return valid


def validateInferenceRequest(requestData: InferenceRequest) -> Union[InferenceRequest, str]:
    """
    Vialidates the inference request

    Returns:
        Union[TrainRequest, dict]: The inference request data or the error to send
    """

    if requestData.shiftUUID is None or requestData.shiftUUID is "":
        return "Your inference request had no shiftUUID"
    
    if requestData.shiftUUID == "PTM":
        return "The UUID cannot be PTM"

    if requestData.usePTM is None:
        return "Your inference request had not indication to use the prebuilt model or not"

    if requestData.prebuiltShiftModel and requestData.prebuiltShiftModel != "PTM":
        try:
            shft = Shift()
            shft.load(encoderPath=os.path.join(current_app.root_path, SHIFT_PATH,
                                               requestData.prebuiltShiftModel),
                      baseDecoderPath=os.path.join(current_app.root_path, SHIFT_PATH,
                                                   requestData.prebuiltShiftModel),
                      maskDecoderPath=os.path.join(current_app.root_path, SHIFT_PATH,
                                                   requestData.prebuiltShiftModel))
        except OSError:
            return "That model does not exist"
    
    return requestData


def validateBaseTrainRequest(requestData: TrainRequest) -> Union[TrainRequest, str]:
    """
    Vialidates the basic version of the train request

    Returns:
        Union[TrainRequest, dict]: The train request data or the error to send
    """

    if requestData.shiftUUID is None or requestData.shiftUUID == "":
        return "Your train request had no shiftUUID"
    
    if requestData.shiftUUID == "PTM":
        return "The UUID cannot be PTM"

    if requestData.usePTM is None:
        return "Your train request had not indication to use the prebuilt model or not"

    if requestData.trainType != "basic" and requestData.trainType != "advanced":
        return "Your train request did not have the correct training type"
    
    return requestData


def validateShiftTitle(title: str) -> bool:
    """
    Determines the validity of the shift title.

    Args:
        title (str): The title to determine the validity of.

    Returns:
        bool: Whether the title is valid or not.
    """
    
    return len(title) >= MINIMUM_SHIFT_TITLE_LENGTH or len(title) <= MAXIMUM_SHIFT_TITLE_LENGTH


def validateShiftTitle(username: str) -> Tuple[bool, str]:
    """
    Determines the validity of the username.

    Args:
        username (str): The username to determine the validity of.

    Returns:
        tuple of bool, str: Whether or not the username is valid with a description message.
    """
    
    if len(username) < MINIMUM_SHIFT_TITLE_LENGTH:
        return False, f'Please make sure your title is more than {MINIMUM_SHIFT_TITLE_LENGTH} character.'

    elif len(username) > MAXIMUM_SHIFT_TITLE_LENGTH:
        return False, f'Please make sure your title is less than {MAXIMUM_SHIFT_TITLE_LENGTH} characters.'
    
    elif not re.match(ALLOWED_SHIFT_TITLE_CHARACTERS, username):
        return False, f"Please make sure your title is only letters, numbers or of these characters'{ALLOWED_SHIFT_TITLE_SPECIAL_CHARACTERS}'"

    return True, 'Success'