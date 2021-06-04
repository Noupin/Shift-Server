#pylint: disable=C0103, C0301
"""
Testing Suite for TFModel class.
"""
__author__ = "Noupin"

#Third Party Imports
import os

#First Party Imports
from src.AI.shift import Shift
from src.utils.MultiImage import MultiImage


def test_StringConstructor():
    image = MultiImage(r"C:\Coding\Projects\Shift Server\src\static\image\default.JPG")

    assert isinstance(image, MultiImage)

