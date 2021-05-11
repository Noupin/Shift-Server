#pylint: disable=C0103, C0301
"""
Routes for the FPn part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from flask import Blueprint
from flask_restful import Api

#First Party Imports
from src.variables.constants import BLUEPRINT_NAMES


fpnBP = Blueprint(BLUEPRINT_NAMES.get("fpn"), __name__)
fpnAPI = Api(fpnBP)

from src.api.FPN.routes.NewShifts import NewShifts
from src.api.FPN.routes.PopularShifts import PopularShifts
from src.api.FPN.routes.FeaturedShifts import FeaturedShifts

fpnAPI.add_resource(NewShifts, "/new")
fpnAPI.add_resource(PopularShifts, "/popular")
fpnAPI.add_resource(FeaturedShifts, "/featured")
