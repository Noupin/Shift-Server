#pylint: disable=C0103, C0301
"""
The MongoDB data model for Token Blocklisting
"""

from __future__ import annotations

__author__ = "Noupin"

#Third Party Imports
from mongoengine import StringField, DateTimeField

#First Party Imports
from src import feryvDB
from src.config import FERYV_DB_ALIAS
from src.variables.constants import ACCESS_EXPIRES



class TokenBlocklist(feryvDB.Document):
    jti = StringField(max_length=36, required=True)
    createdAt = DateTimeField(required=True)

    meta = {
        'db_alias': FERYV_DB_ALIAS,
        'indexes': [
            {
                'fields': ['createdAt'],
                'expireAfterSeconds': ACCESS_EXPIRES.seconds * 2
            }
        ]
    }


    def __repr__(self) -> str:
        return f"TokenBlocklist('{self.id}', '{self.jti}', '{self.created_at}')"


    def __str__(self) -> str:
        return f"TokenBlocklist('{self.id}', '{self.jti}', '{self.created_at}')"
