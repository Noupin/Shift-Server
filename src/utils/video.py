#pylint: disable=C0103, C0301, I1101, R0913, R0902, R0914
"""
The utility functions related to videos
"""
__author__ = "Noupin"

#Third Party Imports
import cv2
import moviepy
import numpy as np
from typing import List
from moviepy import editor as mediaEditor


def extractAudio(video: moviepy.video.io.VideoFileClip.VideoFileClip) -> moviepy.audio.io.AudioFileClip.AudioFileClip:
    """
    Given a video with an audio track the audio track is returned

    Args:
        video (moviepy.video.io.VideoFileClip.VideoFileClip): The video to have the audio extracted
    
    Returns:
        moviepy.audio.io.AudioFileClip.AudioFileClip: The audio track of the video
    """

    if video.audio:
        return video.audio
    
    return mediaEditor.AudioClip(lambda t: [0], duration=video.duration, fps=video.fps)


def insertAudio(video: moviepy.video.io.VideoFileClip.VideoFileClip,
                audio: moviepy.audio.io.AudioFileClip.AudioFileClip) -> moviepy.video.io.VideoFileClip.VideoFileClip:
    """
    Given an audio and video path they will be combined.

    Args:
        video (moviepy.video.io.VideoFileClip.VideoFileClip): The video to have audio inserted into
        audio (moviepy.audio.io.AudioFileClip.AudioFileClip): The audio to be inserted into the video

    Returns:
        moviepy.video.io.VideoFileClip.VideoFileClip: A video clip that has the audio inserted
    """

    return video.set_audio(audio)


def videoToImages(path: str, interval=1, action=None, **kwargs) -> List[np.ndarray]:
    """
    Converts a video into image frames

    Args:
        path (str): Path to the video to be converted to a sequence of images
        action (function): The function to apply to each of the frames of the video. Defaults to None.
    
    Returns:
        list of numpy.ndarray: An array of CV images
    """

    images = []
    frame = 0
    video = cv2.VideoCapture(path)

    print("Total frames:", video.get(cv2.CAP_PROP_FRAME_COUNT))
    for frame in range(int(video.get(cv2.CAP_PROP_FRAME_COUNT))):
        check, image = video.read()
        try:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        except cv2.error as e:
            print("Frame unable to be converted to an image.")
            continue
        if action and frame % interval == 0:
            returnData = action(image=image, **kwargs)
            if type(returnData) == list:
                images += returnData
            else:
                images.append(returnData)
        elif frame % interval == 0:
            images.append(image)
    
    print("Frames grabbed:", len(images))
    
    return images


def loadVideo(path: str) -> moviepy.video.io.VideoFileClip.VideoFileClip:
    """
    Loads a video from path.

    Args:
        path (str): The path to load the video from

    Returns:
        moviepy.video.io.VideoFileClip.VideoFileClip: The loaded video clip
    """

    return mediaEditor.VideoFileClip(path)


def saveVideo(video: moviepy.video.io.VideoFileClip.VideoFileClip, path: str, fps=None) -> None:
    """
    Saves the video to path at fps frame rate

    Args:
        video (moviepy.video.io.VideoFileClip.VideoFileClip): The video to be saved
        path (str): The path to save video
        fps (int, optional): The fps for the video to be saved at. Defaults to None.
    """

    if not fps:
        fps = video.fps

    video.write_videofile(path, fps=fps)
