#pylint: disable=C0103, C0301, I1101, R0913, R0902, R0914
"""
The utility functions related to videos
"""
__author__ = "Noupin"

#Third Party Imports
import cv2
import numpy as np
from moviepy import editor as mediaEditor


def extractAudio(video):
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


def insertAudio(video, audio):
    """
    Given an audio and video path they will be combined.

    Args:
        video (moviepy.video.io.VideoFileClip.VideoFileClip): The video to have audio inserted into
        audio (moviepy.audio.io.AudioFileClip.AudioFileClip): The audio to be inserted into the video

    Returns:
        moviepy.video.io.VideoFileClip.VideoFileClip: A video clip that has the audio inserted
    """

    return video.set_audio(audio)


def videoToImages(path, action=None):
    """
    Converts a video into image frames

    Args:
        path (str): Path to the video to be converted to a sequence of images
        action (function): The function to apply to each of the frames of the video. Defaults to None.
    
    Returns:
        list of numpy.ndarray: An array of CV images
    """

    images = []
    video = cv2.VideoCapture(path)

    for frame in range(int(video.get(cv2.CAP_PROP_FRAME_COUNT))):
        check, image = video.read()
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        images.append(image)
        if action:
            action(image)
    
    return images


def loadVideo(path):
    """
    Loads a video from path.

    Args:
        path (str): The path to load the video from

    Returns:
        moviepy.video.io.VideoFileClip.VideoFileClip: The loaded video clip
    """

    return mediaEditor.VideoFileClip(path)


def saveVideo(video, path, fps=None):
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
