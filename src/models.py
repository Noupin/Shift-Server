#pylint: disable=C0103, C0301
"""
The data models for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from datetime import datetime
from mongoengine import StringField, DateTimeField, EmbeddedDocumentField

#First Party Imports
from src import db, login_manager


@login_manager.user_loader
def load_user(_id):
    return User.object(id=_id).first()


class Shift(db.EmbeddedDocument):
    title = StringField(required=True)
    datePosted = DateTimeField(required=True, default=datetime.utcnow)
    imageFile = StringField(required=True, default='default.jpg')
    encoderFile = StringField(required=True)
    decoderFile = StringField(required=True)

    def __repr__(self):
        return f"Shift('{self.title}, {self.datePosted}, {self.imageFile}, {self.encoderFile}, {self.decoderFile}')"


class User(db.Document):
    username = StringField(required=True, unique=True)
    email = StringField(required=True, unique=True)
    password = StringField(required=True)
    shift = EmbeddedDocumentField(Shift)

    is_active = True

    def get_id(self):
        return User.objects(email=self.email).first().id

    def __repr__(self):
        return f"User('{self.username}, {self.password}')"
