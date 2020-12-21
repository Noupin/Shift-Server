#pylint: disable=C0103, C0301, E1101
"""
The utility functions related to detection
"""
__author__ = "Noupin"

#Third Party Import
import cv2


def detectObject(classifier, image, **kwargs):
    """
    Returns the attributes from the classifier on the given
    image while passing in the kwargs to the classifier.

    Args:
        classifier (function): The classifier function to return the attributes
        image (numpy.ndarray): The image to be passed into classifier
        **kwargs: The arguments to be passed into classifier aswell as whether
                  a conversion to grayscale is needed

    Returns:
        list of int: The atributes from classifier
    """

    if kwargs["gray"]:
        del kwargs["gray"]
        image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        attributes = classifier(image, **kwargs)
    else:
        attributes = classifier(image, **kwargs)
    
    return attributes


def hi():
    #sobel, canny, hystresis
    pass
