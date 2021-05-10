#pylint: disable=C0103, C0301
"""
The Load Data Request Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from typing import List
import werkzeug.datastructures
from marshmallow_dataclass import dataclass


@dataclass(frozen=True)
class LoadDataBodyRequest:
    files: werkzeug.datastructures.FileStorage

@dataclass(frozen=True)
class LoadDataHeaderRequest:
    trainingDataTypes: List[str]

LoadDataBodyRequestDescription = """
The files to be downloaded to the server for the training of the shift model.
"""

LoadDataHeaderRequestDescription = """
A list of file types (base or mask) to determine which folder to save the \
files to. The first type does not matter as it is reserved for the \
original media.
"""
