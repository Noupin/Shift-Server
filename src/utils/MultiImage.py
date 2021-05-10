#pylint: disable=C0103, C0301
"""
Mongo ObjectID Converter
"""
__author__ = "Noupin"

#Third Party Imports
import cv2
import numpy as np
from PIL import Image
from typing import Tuple, Union

#First Party Imports
from src.utils.image import (PILToCV, CVToPIL, resizeImage,
                             loadImage, saveImage, viewImage,
                             encodeImage, cropImage)

class MultiImage:
    """
    Deals with the intricacies of the image types needed for TensorFlow \
    training, OpenCV, and PIL aswell as the different color types of the \
    OpenCV images.
    
    Args:
        image (Union[Image.Image, np.ndarray, str]): The image to be instanced.
    """

    def __init__(self, image: Union[Image.Image, np.ndarray, str]):
        self.PILImage: Image.Image = None
        self.CVImage: np.ndarray = None
        self.CVBGRImage: np.ndarray = None
        self.TFImage: np.ndarray = None
        
        self.update(image)


    def update(self, image: Union[Image.Image, np.ndarray, str]):
        """
        Updates all other forms of the image.

        Args:
            image (Union[Image.Image, np.ndarray]): The image to update all the \
                                                    other image types.
        """

        if isinstance(image, Image.Image):
            self.PILImage = image
            self.CVImage = PILToCV(image).astype(np.uint8)
            self.CVBGRImage = cv2.cvtColor(self.CVImage, cv2.COLOR_RGB2BGR)
        
        if isinstance(image, np.ndarray):
            if image.dtype == np.float32:
                self.CVImage = (image*255).astype(np.uint8)
            else:
                self.CVImage = image.astype(np.uint8)
            self.PILImage = CVToPIL(self.CVImage)
            self.CVBGRImage = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        if isinstance(image, str):
            self.CVImage = loadImage(image).astype(np.uint8)
            self.PILImage = CVToPIL(self.CVImage)
            self.CVBGRImage = cv2.cvtColor(self.CVImage, cv2.COLOR_RGB2BGR)
        
        self.TFImage = (self.CVImage/255.).astype(np.float32)


    def encode(self) -> str:
        """
        Uses the self.PILImage and passes it into the encodeImage \
        function from src.utils.image.

        Returns:
            str: The binary encoded image.
        """

        return encodeImage(self.PILImage)


    def resize(self, width: int=None, height: int=None, keepAR: bool=False, resizer=resizeImage, interpolation: int=cv2.INTER_AREA):
        """
        Resizes the image and updates all other forms of the image.
        
        Args:
            width (int): The desired width of the image. Defaults to None.
            height (int): The desired height of the image. Defaults to None.
            keepAR (bool): Whether or not to preserve the aspect ratio of the \
                           original image. Defaults to False.
            resizer (func): The function used to resize images. Defaults to \
                            resizeImage.
            interpolation (int): The type of interpolation to resize the image \
                                 width. Defaults to cv2.INTER_AREA.
        """

        image = resizer(image=self.CVImage, size=(width, height),
                        keepAR=keepAR, interpolation=interpolation)
        self.update(image)


    def save(self, path: str):
        """
        Saves the image to the desired filepath.
        
        Args:
            path (str): The path to save the image to.
        """

        saveImage(self.CVBGRImage, path) #CV save images in BGR format


    def view(self, **kwargs):
        """
        Displays the image using matplotlib.pyplot.
        
        Args:
            **kwargs (dict[str, Any]): Arguments to be applied to \
                                       matplotlib.pyplot.imshow.
        """

        viewImage(self.CVImage, **kwargs)


    def crop(self, cropArea: Tuple[int]):
        image = cropImage(self.CVImage, cropArea)
        self.update(image)
