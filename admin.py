#pylint: disable=C0103, C0301
"""
The admin actions for Shift
"""
__author__ = "Noupin"

#Third Party Imports
from typing import List
from mongoengine import connect

#First Party Imports
from src.config import Config
from src.models.SQL.Shift import Shift
from src.models.SQL.ShiftCategory import ShiftCategory


def saveCategory(categoryName: str, queryTitles: List[str]):
    shifts = []
    for queryString in queryTitles:
        shifts.append(Shift.query.filter_by.get(title=queryString))

    category = ShiftCategory(name=categoryName, shifts=shifts)
    category.save()

saveCategory("Featured", ["Lizzy"])
