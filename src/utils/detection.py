#pylint: disable=C0103, C0301, E1101
"""
The utility functions related to detection
"""
__author__ = "Noupin"

#Third Party Import
import cv2
import numpy as np
from typing import Iterable, List


def detectObject(classifier, image: np.ndarray, **kwargs) -> Iterable[int]:
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
    
    if kwargs.get("gray"):
        del kwargs["gray"]
        image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        image.flags.writeable = False
        attributes = classifier(image, **kwargs)
        image.flags.writeable = True
    else:
        image.flags.writeable = False
        attributes = classifier(image, **kwargs)
        image.flags.writeable = True
    
    return attributes
