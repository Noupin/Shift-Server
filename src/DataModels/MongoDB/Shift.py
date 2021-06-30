#pylint: disable=C0103, C0301
"""
The MongoDB data model for a Shift
"""
__author__ = "Noupin"

#Third Party Imports
from src.config import SHIFT_DB_ALIAS
from mongoengine import (StringField, BooleanField,
                         UUIDField, IntField,
                         ReferenceField)

#First Party Imports
from src import shiftDB
from src.DataModels.MongoDB.User import User
from src.utils.converter import utcnow_string


class Shift(shiftDB.Document):
    uuid = UUIDField(required=True)
    author = ReferenceField(User, required=True)
    title = StringField(required=True)
    dateCreated = StringField(required=True, default=utcnow_string)
    mediaFilename = StringField(required=True, default='default.jpg')
    baseMediaFilename = StringField(required=True, default='default.jpg')
    maskMediaFilename = StringField(required=True, default='default.jpg')
    private = BooleanField(default=False)
    views = IntField(required=True, default=0)
    verified = BooleanField(default=False)
    
    meta = {
        'db_alias': SHIFT_DB_ALIAS
    }

    def __repr__(self) -> str:
        return f"Shift('{self.uuid}, {self.title}, {self.datePosted}, {self.mediaFilename}')"
