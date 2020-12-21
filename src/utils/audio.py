#pylint: disable=C0103, C0301
"""
The utility functions related to audio
"""
__author__ = "Noupin"

#Third Party Imports
from moviepy import editor as mediaEditor


def loadAudio(path):
    """
    Loads audio from path.

    Args:
        path (str): The path to load the audio from

    Returns:
        moviepy.video.io.AudioFileClip.AudioFileClip: The loaded audio clip
    """

    return mediaEditor.AudioFileClip(path)


def saveAudio(audio, path):
    """
    Saves audio to path.

    Args:
        audio (moviepy.audio.io.AudioFileClip.AudioFileClip): The audio to be saved
        path (str): The path to save the audio to
    """

    audio.write_audiofile(path)
