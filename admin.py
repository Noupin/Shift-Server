#pylint: disable=C0103, C0301
"""
The admin actions for Shift
"""
__author__ = "Noupin"

#Third Party Imports
from typing import List
from src.config import Config, SHIFT_DB_ALIAS
from mongoengine import connect

#First Party Imports
from src.DataModels.MongoDB.Shift import Shift
from src.DataModels.MongoDB.ShiftCategory import ShiftCategory

host = "HOST"
port = "PORT"
db = "DB"

connect(host=f"mongodb://{Config.MONGODB_SETTINGS[0][host]}:{Config.MONGODB_SETTINGS[0][port]}/{Config.MONGODB_SETTINGS[0][db]}",
        alias=SHIFT_DB_ALIAS)

def saveCategory(categoryName: str, queryTitles: List[str]):
    shifts = []
    for queryString in queryTitles:
        shifts.append(Shift.objects.get(title=queryString))

    category = ShiftCategory(name=categoryName, shifts=shifts)
    category.save()

saveCategory("DC", ["baffleck"])
