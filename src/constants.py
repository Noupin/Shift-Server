#pylint: disable=C0103, C0301
"""
Constants for the API
"""
__author__ = "Noupin"

#Third Party Imports
import os
import cv2


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'm4a'}
EXTENSION_FILE_TYPES = {'png': 'image', 'jpg': 'image',
                        'jpeg': 'image', 'gif': 'image',
                        'mp4': 'video', 'm4a': 'video'}
PASSWORD_LENGTH = 6
ALLOWED_NUMBERS = '[0-9]'
ALLOWED_CAPITALS = '[A-Z]'
ALLOWED_SPECIAL_CHARS = '[!@#\$%\^&*\(\)_+{}|:"<>?`\~\-\=\[\]\\\;\',\./]'
FILE_NAME_BYTE_SIZE = 8
VIDEO_FRAME_GRAB_INTERVAL = 5
#Haar Cascade: https://stackoverflow.com/questions/20801015/recommended-values-for-opencv-detectmultiscale-parameters
OBJECT_CLASSIFIER = cv2.CascadeClassifier(os.path.join('shift-env', 'Lib',
                                                       'site-packages', 'cv2',
                                                       'data', 'haarcascade_frontalface_default.xml')
                                          ).detectMultiScale
LARGE_BATCH_SIZE = 64