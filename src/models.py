#pylint: disable=C0103, C0301
"""
The data models for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from datetime import datetime
from mongoengine import StringField, DateTimeField, EmbeddedDocumentField
from flask_login import UserMixin

#First Party Imports
from src import db, login_manager


@login_manager.user_loader
def load_user(userID):
    try:
        return User.objects(id=userID).first()
    except:
        return None


class Shift(db.EmbeddedDocument):
    title = StringField(required=True)
    datePosted = DateTimeField(required=True, default=datetime.utcnow)
    imageFile = StringField(required=True, default='default.jpg')
    encoderFile = StringField(required=True)
    decoderFile = StringField(required=True)

    def __repr__(self):
        return f"Shift('{self.title}, {self.datePosted}, {self.imageFile}, {self.encoderFile}, {self.decoderFile}')"


class User(db.Document, UserMixin):
    username = StringField(required=True, unique=True)
    email = StringField(required=True, unique=True)
    password = StringField(required=True)
    shift = EmbeddedDocumentField(Shift)


    @staticmethod
    def is_authenticated():
        return True

    @staticmethod
    def is_active():
        return True

    @staticmethod
    def is_anonymous():
        return False

    def get_id(self):
        return self.id

    def __repr__(self):
        return f"User('{self.username}, {self.email}')"
    
    def __str__(self):
        return f"User('{self.username}, {self.email}')"
