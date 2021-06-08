#pylint: disable=C0103, C0301
"""
API Validators
"""
__author__ = "https://stackoverflow.com/users/5811078/zipa, Noupin"

#Third Party Imports
import re
import os
import tensorflow as tf
from flask import current_app
from src.AI.shift import Shift
from typing import List, Tuple, Union
from werkzeug.datastructures import FileStorage
from src.DataModels.Request.TrainRequest import TrainRequest
from email_validator import validate_email, EmailNotValidError
from src.DataModels.Request.InferenceRequest import InferenceRequest

#First Party Imports
from src.variables.constants import (
    ALLOWED_EXTENSIONS, PASSWORD_LENGTH, ALLOWED_NUMBERS,
    ALLOWED_CAPITALS, ALLOWED_SPECIAL_CHARS, SHIFT_PATH
    )


def validatePassword(password: str) -> Tuple[bool, str]:
    """
    The given password will be determined valid or invalid

    Args:
        passsword (str): The password to validate

    Returns:
        tuple of bool, str: Whether or not the password is valid with a description message
    """

    valid = True
    msg = "Success"

    if len(password) < PASSWORD_LENGTH:
        valid, msg =  False, "Make sure your password is at lest 8 letters"
    elif not re.search(ALLOWED_NUMBERS, password):
        valid, msg = False, "Make sure your password has a number in it"
    elif not re.search(ALLOWED_CAPITALS, password): 
        valid, msg = False, "Make sure your password has a capital letter in it"
    elif not re.search(ALLOWED_SPECIAL_CHARS, password):
        valid, msg = False, "Make sure your password has a special character in it"

    return valid, msg


def validateEmail(email: str) -> Tuple[bool, str]:
    """
    The given email will be determined valid or invalid

    Args:
        email (str): The email to validate

    Returns:
        tuple of bool, str: Whether or not the email is valid with a description message
    """

    try:
        validate_email(email)
        return True, email
    except EmailNotValidError as e:
        return False, str(e)


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

    if requestData.usePTM is None:
        return "Your inference request had not indication to use the prebuilt model or not"

    if requestData.prebuiltShiftModel:
        try:
            shft = Shift()
            shft.load(encoderPath=os.path.join(current_app.root_path, SHIFT_PATH,
                                  requestData.prebuiltShiftModel),
                      basePath=os.path.join(current_app.root_path, SHIFT_PATH,
                               requestData.prebuiltShiftModel),
                      maskPath=os.path.join(current_app.root_path, SHIFT_PATH,
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

    if requestData.shiftUUID is None or requestData.shiftUUID is "":
        return "Your train request had no shiftUUID"

    if requestData.usePTM is None:
        return "Your train request had not indication to use the prebuilt model or not"

    if requestData.trainType != "basic" and requestData.trainType != "advanced":
        return "Your train request did not have the correct training type"
    
    return requestData


def validateUsername(username: str) -> bool:
    """
    Determines the validity of the username.

    Args:
        username (str): The username to determine the validity of.

    Returns:
        bool: Whether the username is valid or not.
    """
    
    return len(username) > 0


def validateShiftTitle(title: str) -> bool:
    """
    Determines the validity of the shift title.

    Args:
        title (str): The title to determine the validity of.

    Returns:
        bool: Whether the title is valid or not.
    """
    
    return len(title) > 0
