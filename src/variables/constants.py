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
import datetime
import numpy as np
import mediapipe as mp
from mtcnn import MTCNN


MP_FACE_DETECTION = mp.solutions.mediapipe.python.solutions.face_detection

def googleLightweightFacialDetection(img: np.ndarray, **kwargs):
    with MP_FACE_DETECTION.FaceDetection(**kwargs) as faceDetection:
        results = faceDetection.process(img)
        
        rects = []
        
        if not results.detections:
            return rects

        for detection in results.detections:
            bboxC = detection.location_data.relative_bounding_box
            ih, iw, _ = img.shape
            xmin, ymin, width, height = (bboxC.xmin if bboxC.xmin > 0 else 0,
                                         bboxC.ymin if bboxC.ymin > 0 else 0,
                                         bboxC.width if bboxC.width > 0 else 0,
                                         bboxC.height if bboxC.height > 0 else 0,)

            bbox = [int(xmin*iw), int(ymin*ih),
                    int(width*iw), int(height*ih)]

            rects.append(bbox)

    return rects

MTCNN_DETECTOR = MTCNN(scale_factor=0.15)
def mtcnnDetection(pixels: np.ndarray):
    results = MTCNN_DETECTOR.detect_faces(pixels)
    rects = []

    for rect in results:
        rects.append(rect['box'])

    del results
    return rects


#Files
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


#Detection
"""
Haar Cascade for the 70,001 Flikr Images takes 126 minutes for 61,952 of the 70,001
images being an 88.5% yield. On tony.mp4 an average FPS of 19.12 and 99.6% of images detected.

Google TFLite model for the 70,001 Flikr Images takes 70 minutes for ___ of the 70,001
images being an __% yield. On tony.mp4 an average FPS of 51.65 and 88.3% of images detected.

Google MTCNN model on tony.mp4 an average FPS of 1.9 and 99.66% of images detected.
"""
VIDEO_FRAME_GRAB_INTERVAL = 5
#Haar Cascade: https://stackoverflow.com/questions/20801015/recommended-values-for-opencv-detectmultiscale-parameters
GOOGLE_OBJECT_DETECTOR = googleLightweightFacialDetection
GOOGLE_OBJECT_DETECTOR_KWARGS = {'min_detection_confidence': 0.65}

MTCNN_OBJECT_DETECTOR = mtcnnDetection

HAAR_OBJECT_DETECTOR = cv2.CascadeClassifier(os.path.join('shift-env', 'Lib',
                                                          'site-packages', 'cv2',
                                                          'data', 'haarcascade_frontalface_default.xml')
                                            ).detectMultiScale
HAAR_SECONDARY_OBJECT_DETECTOR = cv2.CascadeClassifier(os.path.join('shift-env', 'Lib',
                                                                    'site-packages', 'cv2',
                                                                    'data', 'haarcascade_frontalface_alt.xml')
                                                      ).detectMultiScale
HAAR_OBJECT_DETECTOR_KWARGS = {'scaleFactor': 1.35, 'minNeighbors': 7, 'minSize': (30, 30)}


PRIMARY_OBJECT_CLASSIFIER = HAAR_OBJECT_DETECTOR
SECONDARY_OBJECT_CLASSIFIER = HAAR_SECONDARY_OBJECT_DETECTOR
def combinedDetector(image: np.ndarray, **kwargs):
    grayImage = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    objects = HAAR_OBJECT_DETECTOR(grayImage, **kwargs)

    if len(objects) < 1:
        objects = SECONDARY_OBJECT_CLASSIFIER(grayImage, **kwargs)
    
    return objects

OBJECT_DETECTOR = combinedDetector
OBJECT_DETECTOR_KWARGS = HAAR_OBJECT_DETECTOR_KWARGS


#Image Processing
HUE_ADJUSTMENT = [0, 320/360, 120/360, 215/360] #RGB hue adjustment values

LARGE_BATCH_SIZE = 64

EXHIBIT_IMAGE_COMPRESSION_QUALITY = 50

DEFAULT_FPS = 30
CV_WAIT_KEY = 1

#Facial Landmark Model & Detector
FACIAL_LANDMARK_MODEL = r"shape_predictor_68_face_landmarks.dat"
FACIAL_LANDMARK_DETECTOR = dlib.shape_predictor(FACIAL_LANDMARK_MODEL)

#Folder Paths
IMAGE_PATH = os.path.join("static", "image")
VIDEO_PATH = os.path.join("static", "video")
SHIFT_PATH = os.path.join("static", "shift")
INFERENCE_IMAGE_PATH = os.path.join("static", "inferenceImages")
PTM_ENCODER_REALTIVE_PATH = os.path.join("PTM", "encoder")
PTM_DECODER_REALTIVE_PATH = os.path.join("PTM", "decoder")
PTM_DISCRIMINATOR_REALTIVE_PATH = os.path.join("PTM", "discriminator")

#Blueprint
BLUEPRINT_NAMES = {
    'inference': 'inference',
    'train': 'train',
    'load': 'load',
    'content': 'content',
    'user': 'user',
    'category': 'category',
    'shift': 'shift',
    'authenticate': 'authenticate',
    'extension': 'extension',
}

#Shift Category Limits
AMOUNT_OF_NEW = 10
AMOUNT_OF_POPULAR = 10
PAGINATION_AMOUNT = 30

#OpenAPI
USER_AUTHORIZATION_SCHEME = {"type": "apiKey", "in": "header", "name": "Authorization"}
AUTHORIZATION_SCHEME_NAME = "Bearer"
AUTHORIZATION_TAG = yaml.safe_load(f"""- {AUTHORIZATION_SCHEME_NAME}: []""")
USER_REFRESH_SCHEME = {"type": "apiKey", "in": "cookie", "name": "csrf_refresh_token"}
REFRESH_SCHEME_NAME = "Refresh"
USER_CSRF_REFRESH_SCHEME = {"type": "apiKey", "in": "cookie", "name": "refresh_token_cookie"}
CSRF_REFRESH_SCHEME_NAME = "CSRF_Refresh"
REFRESH_TAG = yaml.safe_load(f"""- {REFRESH_SCHEME_NAME}: []\n- {CSRF_REFRESH_SCHEME_NAME}: []""")
SERVER_URL = "localhost" #os.environ.get("SERVER_URL")
SERVER_PORT = "5000" ##os.environ.get("SERVER_PORT")

#MongoDB
USER_EDITABLE_USER_FIELDS = ["username", "email"]
COSNTANT_USER_FIELDS = ["dateCreated", "id"]
ADMIN_ACCESS_USER_FIELDS = ["verified", "admin", "canTrain"]

USER_EDITABLE_SHIFT_FIELDS = ["title", "private"]
COSNTANT_SHIFT_FIELDS = ["uuid", "id", "author", "dateCreated"]
BACKEND_ACCESS_SHIFT_FIELDS = ["views"]
ADMIN_ACCESS_SHIFT_FIELDS = ["verified"]

FILE_STREAM_TTL = datetime.timedelta(minutes=10).seconds

#Mail
FORGOT_PASSWORD_RESET_TOKEN_EXPIRE = 1800
EMAIL_SENDER = 'login@feryv.com'

#JWT
ACCESS_EXPIRES = datetime.timedelta(minutes=15)

#Redis
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0

#Celery
CELERY_RESULT_BACKEND = "mongodb://localhost:27017"
CELERY_DELETE_SCHEDULE = datetime.timedelta(minutes=10).seconds

#AI Settings
LATENT_SPACE_DIM = 1024
