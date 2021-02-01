#pylint: disable=C0103, C0301
"""
The MongoDB data model for a Shift
"""
__author__ = "Noupin"

#Third Party Imports
from datetime import datetime
from mongoengine import (StringField, DateTimeField,
                         UUIDField, ObjectIdField,
                         BooleanField)

#First Party Imports
from src import db


class Shift(db.Document):
    uuid = UUIDField(required=True)
    userID = ObjectIdField(required=True)
    title = StringField(required=True)
    datePosted = DateTimeField(required=True, default=datetime.utcnow)
    imageFile = StringField(required=True, default='default.jpg')
    encoderFile = StringField(required=True)
    baseDecoderFile = StringField(required=True)
    maskDecoderFile = StringField(required=True)
    private = BooleanField(default=False)

    def __repr__(self) -> str:
        return f"Shift('{self.uuid}, {self.title}, {self.datePosted}, {self.imageFile}')"
