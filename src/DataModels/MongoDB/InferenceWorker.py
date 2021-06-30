#pylint: disable=C0103, C0301
"""
The MongoDB data model for a Train Worker
"""
__author__ = "Noupin"

#Third Party Imports
from datetime import datetime
from src.config import SHIFT_DB_ALIAS
from mongoengine import (StringField, DateTimeField,
                         UUIDField)

#First Party Imports
from src import shiftDB


class InferenceWorker(shiftDB.Document):
    """
    The MongoDB data model for the Inference celery worker.

    Args:
        shiftUUID (UUID, required): The UUID of the shift this worker is associated with.
        workerID (str): The id of the celery worker this MongoDB worker is associated with.
        timeStarted (datetime.datetime): The time the worker was created.
        mediaFilename (str): The filename for the shifted media.
    """

    shiftUUID = UUIDField(required=True)
    workerID = StringField(required=True, default="", unique=True)
    timeStarted = DateTimeField(required=True, default=datetime.utcnow)
    mediaFilename = StringField(required=True, default="")
    baseMediaFilename = StringField(required=True, default="")
    
    meta = {
        'db_alias': SHIFT_DB_ALIAS
    }


    def __repr__(self) -> str:
        return f"InferenceWorker('{self.shiftUUID}, {self.datePosted}')"

    def __str__(self) -> str:
        return f"InferenceWorker('{self.shiftUUID}, {self.datePosted}')"
