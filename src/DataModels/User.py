#pylint: disable=C0103, C0301
"""
The data models for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from mongoengine import StringField, EmbeddedDocumentField
from flask_login import UserMixin

#First Party Imports
from src import db, login_manager
from src.DataModels.Shift import Shift


@login_manager.user_loader
def load_user(userID):
    try:
        return User.objects(id=userID).first()
    except:
        return None


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
