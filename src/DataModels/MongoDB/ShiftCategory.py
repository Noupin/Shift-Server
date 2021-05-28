#pylint: disable=C0103, C0301
"""
The MongoDB data model for a Shifts Category
"""
__author__ = "Noupin"

#Third Party Imports
from enum import unique
from mongoengine import UUIDField, ListField, StringField

#First Party Imports
from src import db


class ShiftCategory(db.Document):
    category = StringField(unique=True, required=True)
    shifts = ListField(UUIDField(), required=True)

    def __repr__(self) -> str:
        return f"ShiftCategory('{self.category}, {self.shifts}')"
