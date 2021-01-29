#pylint: disable=C0103, C0301, E1101
"""
The utility functions related to detection
"""
__author__ = "Noupin"

#Third Party Import
import cv2
import dlib
import numpy as np
import _dlib_pybind11
from typing import List
from imutils import face_utils

#First Party Imports
from src.utils.math import xywhTotrblRectangle
from src.variables.constants import FACIAL_LANDMARK_DETECTOR


def detectObject(classifier, image: np.ndarray, **kwargs) -> List[int]:
    """
    Returns the attributes from the classifier on the given
    image while passing in the kwargs to the classifier.

    Args:
        classifier (function): The classifier function to return the attributes
        image (numpy.ndarray): The image to be passed into classifier
        **kwargs: The arguments to be passed into classifier aswell as whether
                  a conversion to grayscale is needed

    Returns:
        list of int: The atributes from classifier usually a list of rectangles
                     where the objects are in the image
    """

    try:
        kwargs["gray"]
    except KeyError:
        kwargs["gray"] = False
    
    if kwargs["gray"]:
        del kwargs["gray"]
        image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        attributes = classifier(image, **kwargs)
    else:
        del kwargs["gray"]
        attributes = classifier(image, **kwargs)
    
    return attributes


def getFacialLandmarks(image: np.ndarray, objectBoundingBox: _dlib_pybind11.rectangle, xywh2tlbr=True, gray=True) -> List[List[int]]:
    """
    Given an image and the bounding box where the face is in that image facial landmarks
    will be found. If the bounding box is in x, y, width, height terms then it can be
    converted to top-left and bottom-right coordinates. If needed the image can be
    converted to grayscale aswell.

    Args:
        image (np.ndarray): The image to find the facial landmarks in.
        objectBoundingBox (_dlib_pybind11.rectangle): The face bounding box to search within for the facial landmarks.
        xywh2tlbr (bool, optional): Whether or not to convert the bounding box type from x, y,
                                    width, height to top-left and bottom-right. Defaults to True.
        gray (bool, optional): Whether or not the image needs to be converted to grayscale. Defaults to True.

    Returns:
        List[List[int]]: The facial landmarks to be returned following these specifications: 
                             Jaw Points = 0-16
                             Right Brow Points = 17–21
                             Left Brow Points = 22–26
                             Nose Points = 27–35
                             Right Eye Points = 36–41
                             Left Eye Points = 42–47
                             Mouth Points = 48–60
                             Lips Points = 61–67
    """

    if xywh2tlbr:
        objectBoundingBox = xywhTotrblRectangle(objectBoundingBox)

    if gray:
        image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    
    landmarks = FACIAL_LANDMARK_DETECTOR(image, objectBoundingBox)
    landmarks = face_utils.shape_to_np(landmarks)

    return landmarks.tolist()
