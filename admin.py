#pylint: disable=C0103, C0301
"""
The admin actions for Shift
"""
__author__ = "Noupin"

#Third Party Imports
from typing import List
from src.config import Config
from mongoengine import connect

#First Party Imports
from src.DataModels.MongoDB.Shift import Shift
from src.DataModels.MongoDB.ShiftCategory import ShiftCategory

connect(host=Config.MONGO_URI)

def saveCategory(categoryName: str, queryTitles: List[str]):
    shifts = []
    for queryString in queryTitles:
        shifts.append(Shift.objects.get(title=queryString))

    category = ShiftCategory(name=categoryName, shifts=shifts)
    category.save()

#saveCategory("Featured", ["Noup", "AnnaK", "karli"])
