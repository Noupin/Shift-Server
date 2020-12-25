#pylint: disable=C0103, C0301
"""
The data models for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from datetime import datetime
from mongoengine import StringField, DateTimeField

#First Party Imports
from src import db


class Shift(db.EmbeddedDocument):
    title = StringField(required=True)
    datePosted = DateTimeField(required=True, default=datetime.utcnow)
    imageFile = StringField(required=True, default='default.jpg')
    encoderFile = StringField(required=True)
    decoderFile = StringField(required=True)

    def __repr__(self) -> str:
        return f"Shift('{self.title}, {self.datePosted}, {self.imageFile}, {self.encoderFile}, {self.decoderFile}')"
