#pylint: disable=C0103, C0301, R0903, E1101
"""
The configuration variables for the Shift server
"""
__author__ = "Noupin"

#Third Party Imports
import os
import datetime

#First Party Imports
from src.utils.ObjectIdConverter import ObjectIdConverter


class Config:
    SECRET_KEY = open('keys/jwt-key').read()
    MONGO_URI = f"mongodb://{os.environ.get('DB_HOST')}:{os.environ.get('DB_PORT')}/{os.environ.get('DB_PROJECT')}"
    MONGODB_SETTINGS = {
        'db': os.environ.get('DB_PROJECT'),
        'host': os.environ.get('DB_HOST'),
        'port': int(os.environ.get('DB_PORT'))
    }
    OBJECTID = ObjectIdConverter
    USER_DATA_FOLDER = "userData"
    SHIFT_MODELS_FOLDER = os.path.join(USER_DATA_FOLDER, "shiftModels")
    PERMANENT_SESSION_LIFETIME = datetime.timedelta(days=5)
