#pylint: disable=C0103, C0301
"""
The MongoDB data model for a User
"""
__author__ = "Noupin"

#Third Party Imports
from mongoengine import StringField
from flask_login import UserMixin

#First Party Imports
from src import db, login_manager
from src.utils.converter import utcnow_string


class User(db.Document, UserMixin):
    username = StringField(required=True, unique=True)
    email = StringField(required=True, unique=True)
    password = StringField(required=True)
    imagePath = StringField(required=True, default='default.jpg')
    dateCreated = StringField(default=utcnow_string)


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
