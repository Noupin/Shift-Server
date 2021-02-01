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
    shiftUUID = UUIDField(required=True)
    timeStarted = DateTimeField(required=True, default=datetime.utcnow)


    def __repr__(self) -> str:
        return f"InferenceWorker('{self.shiftUUID}, {self.datePosted}')"
