#pylint: disable=C0103, C0301, I1101, R0913, R0902, R0914
"""
The utility functions related to videos
"""
__author__ = "Noupin"

#Third Party Imports
import os
import cv2
import moviepy
import numpy as np
from typing import Generator
from moviepy import editor as mediaEditor

#First Party Import
from src.utils.detection import detectObject


def extractAudio(video: mediaEditor.VideoFileClip) -> mediaEditor.AudioFileClip:
    """
    Given a video with an audio track the audio track is returned

    Args:
        video (mediaEditor.VideoFileClip): The video to have the audio extracted
    
    Returns:
        mediaEditor.AudioFileClip: The audio track of the video
    """

    if video.audio:
        return video.audio
    
    return mediaEditor.AudioFileClip(lambda t: [0], duration=video.duration, fps=video.fps)


def insertAudio(video: mediaEditor.VideoFileClip,
                audio: mediaEditor.AudioFileClip) -> mediaEditor.VideoFileClip:
    """
    Given an audio and video path they will be combined.

    Args:
        video (mediaEditor.VideoFileClip): The video to have audio inserted into
        audio (mediaEditor.AudioFileClip): The audio to be inserted into the video

    Returns:
        mediaEditor.VideoFileClip: A video clip that has the audio inserted
    """

    return video.set_audio(audio)


def videoToImages(path: str, interval=1, action=None, **kwargs) -> Generator[np.ndarray, None, None]:
    """
    Converts a video into image frames

    Args:
        path (str): Path to the video to be converted to a sequence of images
        interval (int, optional): The interval between images to load in. Defaults to 1.
        action (function, optional): The function to apply to each of the frames of the video. Defaults to None.
    
    Returns:
        list of numpy.ndarray: An array of CV images
    """

    try:
        firstImage = kwargs["firstImage"]
        del kwargs["firstImage"]
    except KeyError:
        firstImage = False

    validFrames = 0
    video = cv2.VideoCapture(path)

    for frame in range(int(video.get(cv2.CAP_PROP_FRAME_COUNT))):
        check, image = video.read()

        try:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        except cv2.error as e:
            print("Frame unable to be converted to an image.")
            continue

        if action and validFrames % interval == 0:
            returnData = detectObject(action, image=image, **kwargs)

            if isinstance(returnData, list) and isinstance(returnData[0], np.ndarray): #Checks for list of images
                for image in returnData:
                    yield image
            elif isinstance(returnData, np.ndarray) and returnData.ndim == 3: #Checks for numpy array image
                yield returnData
            elif isinstance(returnData, np.ndarray) and returnData.ndim == 2: #Checks for list of rectangles for object detection areas
                yield image
            else:
                continue

            validFrames += 1

        elif frame % interval == 0:
            yield image
        
        if firstImage:
            break


def loadVideo(path: str) -> mediaEditor.VideoFileClip:
    """
    Loads a video from path.

    Args:
        path (str): The path to load the video from

    Returns:
        mediaEditor.VideoFileClip: The loaded video clip
    """

    return mediaEditor.VideoFileClip(path)


def saveVideo(video: mediaEditor.VideoFileClip, path: str, fps=None, deleteOld=False) -> None:
    """
    Saves the video to path at fps frame rate

    Args:
        video (mediaEditor.VideoFileClip): The video to be saved
        path (str): The path to save video
        fps (int, optional): The fps for the video to be saved at. Defaults to None.
        deleteOld (bool, optional): Whehter or not to delete the old file. Defaults to False.
    """

    if not fps:
        fps = video.fps

    video.write_videofile(path, fps=fps)

    if deleteOld:
        os.remove(video.filename)
