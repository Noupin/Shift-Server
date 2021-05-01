#pylint: disable=C0103, C0301
"""
The MongoDB data model for a Shift
"""
__author__ = "Noupin"

#Third Party Imports
from mongoengine import (StringField, BooleanField,
                         UUIDField, ObjectIdField,
                         IntField)

#First Party Imports
from src import db
from src.utils.converter import utcnow_string


class Shift(db.Document):
    uuid = UUIDField(required=True)
    userID = ObjectIdField(required=True)
    title = StringField(required=True)
    datePosted = StringField(required=True, default=utcnow_string)
    imagePath = StringField(required=True, default='default.jpg')
    encoderPath = StringField(required=True)
    baseDecoderPath = StringField(required=True)
    maskDecoderPath = StringField(required=True)
    private = BooleanField(default=False)
    views = IntField(required=True, default=0)

    def __repr__(self) -> str:
        return f"Shift('{self.uuid}, {self.title}, {self.datePosted}, {self.imagePath}')"
