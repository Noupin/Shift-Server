#pylint: disable=C0103, C0301
"""
The MongoDB data model for a User
"""

from __future__ import annotations

__author__ = "Noupin"

#Third Party Imports
import itsdangerous
from typing import Union
from flask import current_app
from src.config import FERYV_DB_ALIAS
from mongoengine import StringField, BooleanField
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

#First Party Imports
from src import feryvDB
from src.utils.converter import utcnow_string


class User(feryvDB.Document):
    username = StringField(required=True, unique=True)
    email = StringField(required=True, unique=True)
    password = StringField(required=True)
    passwordSalt = StringField(required=True)
    mediaFilename = StringField(required=True, default='default.jpg')
    dateCreated = StringField(default=utcnow_string)
    verified = BooleanField(default=False)
    admin = BooleanField(default=False)
    canTrain = BooleanField(default=False)

    meta = {
        'db_alias': FERYV_DB_ALIAS
    }


    def getResetToken(self, expiresSec=1800):
        s = Serializer(current_app.config["JWT_SECRET_KEY"], expiresSec)
        
        return s.dumps({'user-id': str(self.id)}).decode('utf-8')


    @staticmethod
    def verifyResetToken(token) -> Union[User]:
        s = Serializer(current_app.config["JWT_SECRET_KEY"])
        try:
            userID = s.loads(token)['user-id']
        except itsdangerous.SignatureExpired:
            return None

        return User.objects(id=userID).first()


    def get_id(self) -> str:
        return self.id


    def __repr__(self) -> str:
        return f"User('{self.username}, {self.email}')"


    def __str__(self) -> str:
        return f"User('{self.username}, {self.email}')"
