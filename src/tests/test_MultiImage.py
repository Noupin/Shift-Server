#pylint: disable=C0103, C0301
"""
Testing Suite for MultiImage class.
"""
__author__ = "Noupin"

#Third Party Imports
import numpy as np
from PIL import Image

#First Party Imports
from src.utils.MultiImage import MultiImage
from src.utils.image import loadImage, CVToPIL


multiImage = MultiImage(r"C:\Coding\Projects\Shift Server\src\static\image\default.JPG")


def test_StringConstructor():
    image = MultiImage(r"C:\Coding\Projects\Shift Server\src\static\image\default.JPG")

    assert isinstance(image, MultiImage)


def test_CVConstructor():
    npImage = loadImage(r"C:\Coding\Projects\Shift Server\src\static\image\default.JPG")
    image = MultiImage(npImage)

    assert isinstance(image, MultiImage)


def test_PILConstructor():
    npImage = loadImage(r"C:\Coding\Projects\Shift Server\src\static\image\default.JPG")
    PILImage = CVToPIL(npImage)
    image = MultiImage(PILImage)

    assert isinstance(image, MultiImage)


def test_PILImageType():
    assert isinstance(multiImage.PILImage, Image.Image)


def test_CVImageType():
    assert isinstance(multiImage.CVImage, np.ndarray)
    assert multiImage.CVImage.dtype == np.uint8
    
    assert isinstance(multiImage.CVBGRImage, np.ndarray)
    assert multiImage.CVBGRImage.dtype == np.uint8


def test_TFImageType():
    assert isinstance(multiImage.TFImage, np.ndarray)
    assert multiImage.TFImage.dtype == np.float32


def test_encodeImage():
    assert isinstance(multiImage.encode(), str)
