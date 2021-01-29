#pylint: disable=C0103, C0301
"""
Constants for the API
"""
__author__ = "Noupin"

#Third Party Imports
import os
import cv2
import dlib


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'heic', 'mp4', 'm4a', 'mov'}
EXTENSION_FILE_TYPES = {'': '', 'png': 'image',
                        'jpg': 'image', 'jpeg': 'image',
                        'gif': 'image', 'heic': 'image',
                        'mp4': 'video', 'm4a': 'video',
                        'mov': 'video'}

PASSWORD_LENGTH = 6
ALLOWED_NUMBERS = '[0-9]'
ALLOWED_CAPITALS = '[A-Z]'
ALLOWED_SPECIAL_CHARS = '[!@#\$%\^&*\(\)_+{}|:"<>?`\~\-\=\[\]\\\;\',\./]'

VIDEO_FRAME_GRAB_INTERVAL = 5
#Haar Cascade: https://stackoverflow.com/questions/20801015/recommended-values-for-opencv-detectmultiscale-parameters
OBJECT_CLASSIFIER = cv2.CascadeClassifier(os.path.join('shift-env', 'Lib',
                                                       'site-packages', 'cv2',
                                                       'data', 'haarcascade_frontalface_default.xml')
                                          ).detectMultiScale
HAAR_CASCADE_KWARGS = {'scaleFactor': 1.15, 'minNeighbors': 7, 'minSize': (30, 30)}

LARGE_BATCH_SIZE = 64

#Facial Landmark Model & Detector
FACIAL_LANDMARK_MODEL = r"shape_predictor_68_face_landmarks.dat"
FACIAL_LANDMARK_DETECTOR = dlib.shape_predictor(FACIAL_LANDMARK_MODEL)
