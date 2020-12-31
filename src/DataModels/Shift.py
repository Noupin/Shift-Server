#pylint: disable=C0103, C0301
"""
The data models for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from datetime import datetime
from mongoengine import StringField, DateTimeField, UUIDField

#First Party Imports
from src import db


class Shift(db.EmbeddedDocument):
    uuid = UUIDField(required=True)
    title = StringField(required=True)
    datePosted = DateTimeField(required=True, default=datetime.utcnow)
    imageFile = StringField(required=True, default='default.jpg')
    encoderFile = StringField(required=True)
    baseDecoderFile = StringField(required=True)
    maskDecoderFile = StringField(required=True)

    def __repr__(self) -> str:
        return f"Shift('{self.uuid}, {self.title}, {self.datePosted}, {self.imageFile}, {self.encoderFile}, {self.baseDecoderFile}, {self.maskDecoderFile}')"
