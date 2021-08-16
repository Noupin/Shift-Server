#pylint: disable=C0103, C0301, E1101
"""
The decorator for use confirmation
"""
__author__ = "Noupin"

#Third Party Imports
from functools import wraps
from flask_jwt_extended import current_user

#Third Party Imports
from src.models.Response.DefaultResponse import DefaultResponse


def confirmationRequired(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.feryvUser.confirmed is False:
            return DefaultResponse(msg="Please confirm your account.")

        return func(*args, **kwargs)

    return decorated_function
