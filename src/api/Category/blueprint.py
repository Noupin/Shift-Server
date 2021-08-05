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


categoryBP = Blueprint(BLUEPRINT_NAMES.get("category"), __name__)
categoryAPI = Api(categoryBP)

from src.api.category.routes.NewShifts import NewShifts
from src.api.category.routes.Categories import Categories
from src.api.category.routes.PopularShifts import PopularShifts
from src.api.category.routes.ShiftCategory import ShiftCategory

categoryAPI.add_resource(NewShifts, "/new")
categoryAPI.add_resource(Categories, "/categories")
categoryAPI.add_resource(PopularShifts, "/popular")
categoryAPI.add_resource(ShiftCategory, "/<string:categoryName>")
