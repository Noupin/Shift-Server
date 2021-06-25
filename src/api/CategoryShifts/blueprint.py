#pylint: disable=C0103, C0301
"""
Routes for the Shift Category part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from flask import Blueprint
from flask_restful import Api

#First Party Imports
from src.variables.constants import BLUEPRINT_NAMES


categoryShiftBP = Blueprint(BLUEPRINT_NAMES.get("categoryShifts"), __name__)
categoryShiftAPI = Api(categoryShiftBP)

from src.api.CategoryShifts.routes.Category import Category
from src.api.CategoryShifts.routes.NewShifts import NewShifts
from src.api.CategoryShifts.routes.PopularShifts import PopularShifts

categoryShiftAPI.add_resource(NewShifts, "/new")
categoryShiftAPI.add_resource(PopularShifts, "/popular")
categoryShiftAPI.add_resource(Category, "/<string:categoryName>")
