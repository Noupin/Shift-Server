#pylint: disable=C0103, C0301
"""
The data models for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
import mongoengine
from mongoengine import StringField, EmbeddedDocumentListField
from flask_login import UserMixin

#First Party Imports
from src import db, login_manager
from src.DataModels.MongoDB.Shift import Shift


class User(db.Document, UserMixin):
    username = StringField(required=True, unique=True)
    email = StringField(required=True, unique=True)
    password = StringField(required=True)
    shifts = EmbeddedDocumentListField(Shift)


    @staticmethod
    def is_authenticated() -> bool:
        return True


    @staticmethod
    def is_active() -> bool:
        return True


    @staticmethod
    def is_anonymous() -> bool:
        return False


    def get_id(self) -> str:
        return self.id


    def __repr__(self) -> str:
        return f"User('{self.username}, {self.email}')"
    

    def __str__(self) -> str:
        return f"User('{self.username}, {self.email}')"


@login_manager.user_loader
def load_user(userID: str) -> User:
    try:
        return User.objects(id=userID).first()
    except:
        return None
