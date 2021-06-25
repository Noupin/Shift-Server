#pylint: disable=C0103, C0301
"""
The MongoDB data model for a Shifts Category
"""
__author__ = "Noupin"

#Third Party Imports
from typing import List
from src.DataModels.MongoDB.Shift import Shift
from mongoengine import ReferenceField, ListField, StringField

#First Party Imports
from src import db


class ShiftCategory(db.Document):
    name = StringField(unique=True, required=True)
    shifts = ListField(ReferenceField(Shift), required=True)

    def __repr__(self) -> str:
        return f"ShiftCategory('{self.name}, {self.shifts}')"
