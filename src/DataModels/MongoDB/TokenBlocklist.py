#pylint: disable=C0103, C0301
"""
The MongoDB data model for a User
"""

from __future__ import annotations
from src.variables.constants import ACCESS_EXPIRES

__author__ = "Noupin"

#Third Party Imports
from src.config import FERYV_DB_ALIAS
from mongoengine import IntField, StringField, DateTimeField

#First Party Imports
from src import feryvDB


class TokenBlocklist(feryvDB.Document):
    jti = StringField(max_length=36, required=True)
    createdAt = DateTimeField(required=True)
    expireAfterSeconds = IntField(default=ACCESS_EXPIRES.seconds)

    meta = {
        'db_alias': FERYV_DB_ALIAS,
    }


    def __repr__(self) -> str:
        return f"TokenBlocklist('{self.id}', '{self.jti}', '{self.created_at}')"


    def __str__(self) -> str:
        return f"TokenBlocklist('{self.id}', '{self.jti}', '{self.created_at}')"
