#pylint: disable=C0103, C0301
"""
The MongoDB data model for a Featured shift
"""
__author__ = "Noupin"

#Third Party Imports
from mongoengine import UUIDField

#First Party Imports
from src import db


class Featured(db.Document):
    uuid = UUIDField(required=True)

    def __repr__(self) -> str:
        return f"Featured('{self.uuid}')"
