#pylint: disable=C0103, C0301
"""
Constants for the API
"""
__author__ = "Noupin"

#Third Party Imports
import os
import cv2
import dlib
import yaml
import string
import piexif
import numpy as np
import mediapipe as mp


def googleLightweightFacialDetection(img: np.ndarray, **kwargs):
    mpFaceDetection = mp.solutions.mediapipe.python.solutions.face_detection
    
    with mpFaceDetection.FaceDetection(**kwargs) as faceDetection:
        results = faceDetection.process(img)
        
        rects = []
        
        if not results.detections:
            return rects

        for detection in results.detections:
            bboxC = detection.location_data.relative_bounding_box
            ih, iw, _ = img.shape

            bbox = [abs(int(bboxC.xmin*iw)), abs(int(bboxC.ymin*ih)),
                    abs(int(bboxC.width*iw)), abs(int(bboxC.height*ih))]
            rects.append(bbox)
        
        return rects


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'heic', 'mp4', 'm4a', 'mov'}
EXTENSION_FILE_TYPES = {'': '', 'png': 'image',
                        'jpg': 'image', 'jpeg': 'image',
                        'gif': 'image', 'heic': 'image',
                        'mp4': 'video', 'm4a': 'video',
                        'mov': 'video'}

#Metadata
SHIFT_IMAGE_METADATA_KEY = "0th"
SHIFT_IMAGE_METADATA_VALUE = {piexif.ImageIFD.ProcessingSoftware: u"Shift"}
SHIFT_VIDEO_METADATA_KEY = "\xa9cmt"
SHIFT_VIDEO_METADATA_VALUE = "Shift"

#Password
MINIMUM_PASSWORD_LENGTH = 6
ALLOWED_NUMBERS = '[0-9]'
ALLOWED_CAPITALS = '[A-Z]'
ALLOWED_SPECIAL_CHARS = '[!@#\$%\^&*\(\)_+{}|:"<>?`\~\-\=\[\]\\\;\',\./]'
PEPPER_CHARACTERS = list(string.ascii_uppercase) + list(string.ascii_lowercase)

"""
Haar Cascade for the 70,001 Flikr Images takes 126 minutes for 61,952 of the 70,001
images being an 88.5% yield.

Google TFLite model for the 70,001 Flikr Images takes 70 minutes for ___ of the 70,001
images being an __% yield.
"""
VIDEO_FRAME_GRAB_INTERVAL = 5
#Haar Cascade: https://stackoverflow.com/questions/20801015/recommended-values-for-opencv-detectmultiscale-parameters
TEST_OBJECT_CLASSIFIER = googleLightweightFacialDetection
TEST_OBJECT_CLASSIFIER_KWARGS = {'min_detection_confidence': 0.7}

OBJECT_CLASSIFIER = cv2.CascadeClassifier(os.path.join('shift-env', 'Lib',
                                                       'site-packages', 'cv2',
                                                       'data', 'haarcascade_frontalface_default.xml')
                                          ).detectMultiScale
OBJECT_CLASSIFIER_KWARGS = {'scaleFactor': 1.15, 'minNeighbors': 7, 'minSize': (30, 30)}
CV_WAIT_KEY = 1

HUE_ADJUSTMENT = [0, 320/360, 120/360, 215/360] #RGB hue adjustment values

LARGE_BATCH_SIZE = 64

EXHIBIT_IMAGE_COMPRESSION_QUALITY = 50

DEFAULT_FPS = 30

#Facial Landmark Model & Detector
FACIAL_LANDMARK_MODEL = r"shape_predictor_68_face_landmarks.dat"
FACIAL_LANDMARK_DETECTOR = dlib.shape_predictor(FACIAL_LANDMARK_MODEL)

#Folder Paths
IMAGE_PATH = os.path.join("static", "image")
VIDEO_PATH = os.path.join("static", "video")
SHIFT_PATH = os.path.join("static", "shift")
PTM_ENCODER_REALTIVE_PATH = os.path.join("PTM", "encoder")
PTM_DECODER_REALTIVE_PATH = os.path.join("PTM", "decoder")
PTM_DISCRIMINATOR_REALTIVE_PATH = os.path.join("PTM", "discriminator")

BLUEPRINT_NAMES = {
    'inference': 'inference',
    'train': 'train',
    'load': 'load',
    'content': 'content',
    'user': 'user',
    'category': 'category',
    'shift': 'shift',
    'authenticate': 'authenticate'
}

#Shift Category Limits
ANMOUNT_OF_NEW = 10
AMOUNT_OF_POPULAR = 10
PAGINATION_AMOUNT = 30

#OpenAPI
USER_AUTH_SCHEME = {"type": "apiKey", "in": "header", "name": "session"}
SECURITY_SCHEME_NAME = "UserAuth"
SECURITY_TAG = yaml.safe_load(f"""- {SECURITY_SCHEME_NAME}: []""")
SERVER_URL = "localhost" #os.environ.get("SERVER_URL")
SERVER_PORT = "5000" ##os.environ.get("SERVER_PORT")

#MongoDB
USER_EDITABLE_USER_FIELDS = ["username", "email"]
COSNTANT_USER_FIELDS = ["dateCreated", "id"]
ADMIN_ACCESS_USER_FIELDS = ["verified", "admin"]

USER_EDITABLE_SHIFT_FIELDS = ["title", "private"]
COSNTANT_SHIFT_FIELDS = ["uuid", "id", "author", "dateCreated"]
BACKEND_ACCESS_SHIFT_FIELDS = ["views"]
ADMIN_ACCESS_SHIFT_FIELDS = ["verified"]

#Mail
FORGOT_PASSWORD_RESET_TOKEN_EXPIRE = 1800
EMAIL_SENDER = 'login@feryv.com'
