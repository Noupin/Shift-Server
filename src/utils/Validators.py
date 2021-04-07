#pylint: disable=C0103, C0301
"""
API Validators
"""
__author__ = "https://stackoverflow.com/users/5811078/zipa, Noupin"

#Third Party Imports
import re
import werkzeug
from typing import Tuple
from email_validator import validate_email, EmailNotValidError

#First Party Imports
from src.variables.constants import (
    ALLOWED_EXTENSIONS, PASSWORD_LENGTH, ALLOWED_NUMBERS,
    ALLOWED_CAPITALS, ALLOWED_SPECIAL_CHARS
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


def validateFileRequest(fileDict: werkzeug.datastructures.MultiDict, fileIndicator="file") -> bool:
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
        if currentFile.find(fileIndicator) != -1:
            continue

        valid = False
        break
    
    return valid
