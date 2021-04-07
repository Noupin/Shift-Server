#pylint: disable=C0103, C0301
"""
The MongoDB data model for a Train Worker
"""
__author__ = "Noupin"

#Third Party Imports
from datetime import datetime
from mongoengine import (StringField, DateTimeField,
                         UUIDField, BooleanField,
                         ListField)

#First Party Imports
from src import db


class TrainWorker(db.Document):
    """
    The MongoDB data model for the Train celery worker.

    Args:
        shiftUUID (UUID, required): The UUID of the shift this worker is associated with.
        workerID (str): The id of the celery worker this MongoDB worker is associated with.
        timeStarted (datetime.datetime): The time the worker was created.
        training (bool): Whether or not the worker is training or not.
        inferencing (bool): Whether or not the worker is inferencing or not.
        imagesUpdated (bool): Whether or not the exhibit images are updated and ready to be sent to the front-end.
        exhibitImages (list of str): The binary encoded images to be sent to the frontend.
    """

    shiftUUID = UUIDField(required=True, unique=True)
    workerID = StringField(required=True, default="", unique=True)
    timeStarted = DateTimeField(required=True, default=datetime.utcnow)
    training = BooleanField(required=True, default=False)
    inferencing = BooleanField(required=True, default=False)
    imagesUpdated = BooleanField(required=True, default=False)
    exhibitImages = ListField(StringField())


    def __repr__(self) -> str:
        return f"TrainWorker('shiftUUID: {self.shiftUUID}, workerID: {self.workerID}, training: {self.training}, inferencing: {self.inferencing}')"
    
    def __str__(self) -> str:
        return f"TrainWorker('shiftUUID: {self.shiftUUID}, workerID: {self.workerID}, training: {self.training}, inferencing: {self.inferencing}')"
