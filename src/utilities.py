#pylint: disable=C0103, C0301, R0903, E1101
"""
No-self-use functions for Shift
"""
__author__ = "Noupin, KeeKee"

#Third Party Imports
import os
import re
import time
import json
import math
import psutil
import socket
import cv2
import tensorflow as tf

#First Party Imports
from tunable import Tunable
from constants import Constants


def memoryGrowth(growth=True):
    """
    Fixes Blas-GEMM error
    Allows memory growth for TensorFlow
    """

    gpus = tf.config.experimental.list_physical_devices('GPU')
    if gpus:
        try:
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, growth)
        except RuntimeError as e:
            print(e)

def checkPathExistsAndMake(path, full=False):
    """
    Checks if the given folder path exists and if it doesnt it creates it
    """

    if path.split("\\")[-1] not in os.listdir(Constants.pyProjectDir) and not full:
        os.mkdir(os.path.join(Constants.pyProjectDir, path.split("\\")[-1]))

    elif full and path.split("\\")[-1] not in os.listdir("\\".join(path.split("\\")[:-1])):
        os.mkdir(os.path.join("\\".join(path.split("\\")[:-1]), path.split("\\")[-1]))

def atoi(text):
    """
    Checks integer versus non-integer
    """

    return int(text) if text.isdigit() else text

def natural_keys(text):
    """
    Keys for natural sorting of alphanumeric lists
    """

    return [atoi(c) for c in re.split(r'(\d+)', text)]

def recordCamera(length, vidOutPath):
    """
    Records a video using a connected camera at a tunable fps
    """

    camera = cv2.VideoCapture(0)

    codec = cv2.VideoWriter_fourcc(*'XVID')

    camera.set(cv2.CAP_PROP_FOURCC, codec)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    camera.set(cv2.CAP_PROP_FPS, Tunable.tunableDict["cameraFPS"])

    out = cv2.VideoWriter(vidOutPath+"output.mp4",
                          codec,
                          camera.get(cv2.CAP_PROP_FPS),
                          (Tunable.tunableDict["imgX"], Tunable.tunableDict["imgX"]))

    start = time.time()
    current = time.time()
    count = 0
    while (current - start) <= length:
        _, frame = camera.read()
        count += 1
        frame = cv2.flip(frame, 1)

        xStart = int((camera.get(cv2.CAP_PROP_FRAME_WIDTH)/2)-(Tunable.tunableDict["cameraX"]/2))
        yStart = int((camera.get(cv2.CAP_PROP_FRAME_HEIGHT)/2)-(Tunable.tunableDict["cameraY"]/2))
        frame = frame[yStart:yStart+Tunable.tunableDict["cameraY"], xStart:xStart+Tunable.tunableDict["cameraX"]]

        out.write(frame)
        cv2.imshow("Camera", frame)
        current = time.time()

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    print(current-start)

    camera.release()
    out.release()
    cv2.destroyAllWindows()

def checkPortOpen(port, ip="localhost"):
    """
    Checks if a given port is open on an IP
    """

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return not s.connect_ex((ip, port)) == 0

def changeJSON(key, value):
    """
    Takes a key and a value to change the tunable JSON file
    """

    with open(os.path.join(Constants.pyProjectDir, "tunable.json")) as jsonFile:
        tunableDict = json.load(jsonFile)

    tunableDict[key] = value

    with open(os.path.join(Constants.pyProjectDir, "tunable.json"), 'w') as jsonFile:
        json.dump(tunableDict, jsonFile)

def getImageMemBufferSize(imageSizes):
    """
    Given a list of tuples containing image x and y sizes the
    number of images that can be held in the avaiable computer
    memory will be returned
    """

    availableMem = psutil.virtual_memory()[4]
    usingMem = (availableMem*Tunable.tunableDict["memoryFrac"])-500_000_000 #Leaving 500MB of memory

    typesOfImages = len(imageSizes)
    maxImgSize = (0, 0)
    smallerImgSize = (0, 0)
    for size in imageSizes:
        if size[0]*size[1] > maxImgSize[0]*maxImgSize[1]:
            smallerImgSize = maxImgSize
            maxImgSize = size
        elif size[0]*size[1] > smallerImgSize[0]*smallerImgSize[1]:
            smallerImgSize = size

    largeImageByteSize = (maxImgSize[0]*maxImgSize[1]*3*32)/8
    smallImageByteSize = (smallerImgSize[0]*smallerImgSize[1]*3*32)/8

    maximumImageCount = math.floor(usingMem/largeImageByteSize)
    smallImagesPerLargeImage = int(math.floor(largeImageByteSize/smallImageByteSize))

    if smallImagesPerLargeImage == 1:
        imagesToTake = math.ceil(maximumImageCount/(smallImagesPerLargeImage*typesOfImages))
    else:
        imagesToTake = math.ceil(maximumImageCount/smallImagesPerLargeImage)

    equalImageCount = maximumImageCount-(imagesToTake*(typesOfImages-1))

    return equalImageCount
