#pylint: disable=C0103, C0301
"""
The MongoDB data model for a Train Worker
"""
__author__ = "Noupin"

#Third Party Imports
from datetime import datetime
from mongoengine import (StringField, DateTimeField,
                         UUIDField, ObjectIdField,
                         BooleanField)

#First Party Imports
from src import db


class InferenceWorker(db.Document):
    """
    The MongoDB data model for the Inference celery worker.

    Args:
        shiftUUID (UUID, required): The UUID of the shift this worker is associated with.
        workerID (str): The id of the celery worker this MongoDB worker is associated with.
        timeStarted (datetime.datetime): The time the worker was created.
    """

    shiftUUID = UUIDField(required=True)
    workerID = StringField(required=True, default="", unique=True)
    timeStarted = DateTimeField(required=True, default=datetime.utcnow)


    def __repr__(self) -> str:
        return f"InferenceWorker('{self.shiftUUID}, {self.datePosted}')"

    def __str__(self) -> str:
        return f"InferenceWorker('{self.shiftUUID}, {self.datePosted}')"
