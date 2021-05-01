#pylint: disable=C0103, C0301
"""
The utility functions related to converting between types
"""
__author__ = "Noupin"

#Third Party Imports
from datetime import datetime


def utcnow_string():
    return str(datetime.utcnow())
