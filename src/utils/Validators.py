#pylint: disable=C0103, C0301
"""
API Validator
"""
__author__ = "https://stackoverflow.com/users/5811078/zipa"

#Third Party Imports
import re
from email_validator import validate_email, EmailNotValidError


def validatePassword(password):
    """
    The given password will be determined valid or invalid

    Args:
        passsword (str): The password to validate

    Returns:
        (bool, str): Whether or not the password is valid with a description message
    """

    valid = True
    msg = "Success"

    if len(password) < 6:
        valid, msg =  False, "Make sure your password is at lest 8 letters"
    elif not re.search('[0-9]', password):
        valid, msg = False, "Make sure your password has a number in it"
    elif not re.search('[A-Z]', password): 
        valid, msg = False, "Make sure your password has a capital letter in it"
    elif not re.search('[!@#\$%\^&*\(\)_+{}|:"<>?`\~\-\=\[\]\\\;\',\./]', password):
        valid, msg = False, "Make sure your password has a special character in it"

    return valid, msg

def validateEmail(email):
    """
    The given email will be determined valid or invalid

    Args:
        email (str): The email to validate

    Returns:
        (bool, str): Whether or not the email is valid with a description message
    """

    try:
        validate_email(email)
        return True, email
    except EmailNotValidError as e:
        return False, str(e)