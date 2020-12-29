#pylint: disable=C0103, C0301, R0903
"""
The utility functions related to files
"""
__author__ = "Noupin"

#Third Party Imports
import uuid
import base64


def generateUniqueFilename(generator=uuid.uuid4, urlSafe=False) -> str:
    """
    Generates a unique filename.

    Args:
        generator (function): The function to use for the unique generation.
        urlSafe (bool): Whether the filename needs to be url safe or not. Defaults to False.

    Returns:
        str: The uniquely generated filename
    """

    uuid_ = generator()
    finalUUID = (str(uuid_), str(base64.urlsafe_b64encode(uuid_.bytes)).replace('=', ''))[urlSafe]

    return finalUUID
