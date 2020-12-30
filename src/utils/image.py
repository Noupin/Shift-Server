#pylint: disable=C0103, C0301, E1101
"""
The utility functions related to images
"""
__author__ = "Noupin"

#Third Party Imports
import io
import cv2
import base64
import numpy as np
from PIL import Image
from typing import List, Tuple
from colorama import Fore
import matplotlib.pyplot as plt

#First Party Imports
from src.Exceptions.CVToPIL import CVToPILError


def PILToCV(image: Image.Image) -> np.ndarray:
    """
    Given a PIL image it will be converted to a CV image

    Args:
        image (PIL.Image.Image): The PIL Image to be converted to CV

    Returns:
        numpy.ndarray: The CV image
    """

    image = np.asarray(image)

    return image


def CVToPIL(image: np.ndarray) -> Image.Image:
    """
    Given a CV image it will be converted to a PIL image

    Args:
        image (numpy.ndarray): The CV image to be converted to PIL

    Returns:
        PIL.Image.Image: The PIL image
    """

    if type(image) == Image.Image:
        try:
            raise PILToCVError(image)
        except PILToCVError as e:
            print(e)
            print(Fore.GREEN + "Conversion skipped." + Fore.RESET)
            return image

    image = Image.fromarray(image)

    return image


def loadImage(path: str) -> np.ndarray:
    """
    Given a path the image is loaded and converted to the RGB color space

    Args:
        path (str): The path to the image to be loaded

    Returns:
        numpy.ndarray: The RGB CV image
    """

    image = cv2.imread(path)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    return image


def saveImage(image: np.ndarray, path: str) -> None:
    """
    Saves the image to the given path

    Args:
        image (numpy.ndarray): The image to be saved
        path (str): The path to where the file is saved
    """

    cv2.imwrite(path, image)


def resizeImage(image: np.ndarray, size: Tuple[int], keepAR=True) -> np.ndarray:
    """
    Given a cv2 image it is resized to the given size

    Args:
        image (numpy.ndarray): The image object to be resized
        size (tuple of int): A tuple of the desired x and y dimension
        keepAR (bool): Whether or not to keep the aspect ratio of the image

    Returns:
        numpy.ndarray: The resized CV image
    """

    image = PILToCV(image)

    if keepAR:
        image = cv2.resize(image, size)
    else:
        image = cv2.resize(image, size, interpolation=cv2.INTER_AREA)

    return image


def cropImage(image: np.ndarray, cropArea: Tuple[int]) -> np.ndarray:
    """
    Crops the crop area out of image

    Args:
        image (numpy.ndarray): The image to be cropped
        cropArea (tuple of int): The x, y, width and height values of
                                 the rectange to be cropped from image

    Returns:
        numpy.ndarray: The cropped portion of the image
    """

    x, y, width, height = cropArea

    return image[int(y):int(y+height), int(x):int(x+width)]


def viewImage(image) -> None:
    """
    Given a CV image or a PIL image it will be previewed using matplotlib

    Args:
        image (PIL.Image.Image or numpy.ndarray): The image to be displayed
    """

    plt.imshow(image)
    plt.show()


def encodeImage(image) -> str:
    """
    Takes in an image array then encodes it as a bytestring to be streamed through JSON to JavaScript.

    Args:
        image (numpy.ndarray or PIL.Image.Image): The image to be converted to binary string

    Returns:
        str: The binary encoding of the image
    """

    image = PILToCV(image)

    image = image.astype(np.uint8)
    image = CVToPIL(image)

    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    imageString = base64.b64encode(buffered.getvalue())
    encodedImage = imageString.decode('utf-8')

    return encodedImage


def decodeImage(encodedImage: str) -> np.ndarray:
    """
    Given an encoded image as a binary string it will be decoded into a CV image

    Args:
        encodedImage (str): The encoded image binary string

    Returns:
        numpy.ndarray: The decoded image
    """

    decodedImage = base64.b64decode(encodedImage)
    image = Image.open(io.BytesIO(decodedImage))

    return image


def blendImageAndColor(image, colorCode: int) -> np.ndarray:
    """
    Given an input image an augmented image is returned.

    Args:
        image (PIL.Image.Image or numpy.ndarray): The image to be masked by a given color
        colorCode (int): The corresponding integer to the colorMasks values

    Returns:
        numpy.ndarray: The color masked image
    """

    colorMasks = {0: (255, 0, 0), #Red
                  1: (0, 255, 0), #Green
                  2: (0, 0, 255), #Blue
                  3: (0, 0, 0), #Black
                  4: (255, 255, 255)} # White
    alphaLevels = {0: 0.3, #Red alpha level
                   1: 0.3, #Green alpha level
                   2: 0.3, #Blue alpha level
                   3: 0.7, #Black alpha level
                   4: 0.7} #White alpha level

    image = CVToPIL(image)
    colorImage = Image.new("RGB", image.size,
                           colorMasks[colorCode])
    augmenetedImage = Image.blend(image, colorImage, alphaLevels[colorCode])

    image = PILToCV(augmenetedImage)

    return image


def flipImage(image, flipCode: str) -> np.ndarray:
    """
    The image will be flipped by the corresponding flip code.

    Args:
        image (PIL.Image.Image or numpy.ndarray): [description]
        flipCode (str): The corresponding string to the flip values

    Returns:
        numpy.ndarray: The flipped image
    """

    flipMap = {"x": 0,
               "y": 1,
               "xy": -1,
               "yx": -1}
    image = PILToCV(image)

    return cv2.flip(image, flipMap[flipCode])


def imagesToVideo(images: List[np.ndarray], outPath: str, fps: float) -> None:
    """
    Given a path with all of the image arrays a .mp4 video will be exported

    Args:
        images (list of numpy.ndarray): An array of cv images
        outPath (str): The path to save the video to
        fps (float): The fps at which to combine the video at
    """

    height, width, colorDim = images[0].shape

    codec = cv2.VideoWriter_fourcc(*'H264') #H264, X264, MP42, MP4A
    videoWrite = cv2.VideoWriter(outPath,
                                codec,
                                fps,
                                (width, height))

    for image in images:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        videoWrite.write(image)

    videoWrite.release()
    cv2.destroyAllWindows()
