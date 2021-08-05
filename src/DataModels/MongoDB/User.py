#pylint: disable=C0103, C0301
"""
The MongoDB data model for a User
"""

from __future__ import annotations

from mongoengine.fields import ReferenceField

from src.variables.constants import CONFIRM_EMAIL_TOKEN_EXPIRE

__author__ = "Noupin"

#Third Party Imports
import itsdangerous
from flask import current_app
from datetime import datetime
from typing import Union, Tuple
from src.config import FERYV_DB_ALIAS
from src.DataModels.MongoDB.Subscription import Subscription
from itsdangerous import (JSONWebSignatureSerializer,
                          TimedJSONWebSignatureSerializer as Serializer)
from mongoengine import StringField, BooleanField, DateTimeField, MapField

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
    confirmed = BooleanField(default=False)
    createdAt = DateTimeField(default=datetime.utcnow)
    subscriptions = MapField(ReferenceField(Subscription))

    meta = {
        'db_alias': FERYV_DB_ALIAS,
        'indexes': [
            {
                'fields': ['createdAt'],
                'expireAfterSeconds': int(CONFIRM_EMAIL_TOKEN_EXPIRE*1.5),
                'partialFilterExpression': {
                    'confirmed': False
                },
            }
        ],
    }


    def getResetToken(self, expiresSec=1800) -> JSONWebSignatureSerializer:
        s = Serializer(current_app.config["JWT_SECRET_KEY"], expiresSec)
        
        return s.dumps({'user-id': str(self.id)}).decode('utf-8')


    @staticmethod
    def verifyResetToken(token) -> Union[User]:
        s = Serializer(current_app.config["JWT_SECRET_KEY"])
        try:
            userID = s.loads(token)['user-id']
        except (itsdangerous.SignatureExpired, itsdangerous.BadSignature, KeyError):
            return None

        return User.objects(id=userID).first()


    def getConfirmationToken(self, expiresSec=1800) -> JSONWebSignatureSerializer:
        s = Serializer(current_app.config["JWT_SECRET_KEY"], expiresSec)
        
        return s.dumps({'email': str(self.email)}).decode('utf-8')


    @staticmethod
    def verifyConfimationToken(token) -> Tuple[str, Union[User]]:
        s = Serializer(current_app.config["JWT_SECRET_KEY"])
        try:
            email = s.loads(token)['email']
        except (itsdangerous.SignatureExpired, itsdangerous.BadSignature, KeyError):
            return None, None

        return email, User.objects(email=email).first()
    
    
    def getChangeEmailToken(self, nextEmail: str, expiresSec=1800) -> JSONWebSignatureSerializer:
        s = Serializer(current_app.config["JWT_SECRET_KEY"], expiresSec)
        
        return s.dumps({'email': str(self.email), 'nextEmail': nextEmail}).decode('utf-8')


    @staticmethod
    def verifyChangeEmailToken(token) -> Tuple[str, Union[User]]:
        s = Serializer(current_app.config["JWT_SECRET_KEY"])
        try:
            loadedMessage = s.loads(token)
            email = loadedMessage['email']
            nextEmail = loadedMessage['nextEmail']
        except (itsdangerous.SignatureExpired, itsdangerous.BadSignature, KeyError):
            return None, None

        return nextEmail, User.objects(email=email).first()


    def get_id(self) -> str:
        return self.id


    def __repr__(self) -> str:
        return f"User('{self.username}, {self.email}')"


    def __str__(self) -> str:
        return f"User('{self.username}, {self.email}')"
