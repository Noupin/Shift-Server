#pylint: disable=C0103, C0301
"""
Routes for the Shift part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from flask import Blueprint
from flask_restful import Api

#First Party Imports
from src.variables.constants import BLUEPRINT_NAMES


shiftBP = Blueprint(BLUEPRINT_NAMES.get("shift"), __name__)
shiftAPI = Api(shiftBP)

from src.api.shift.routes.IndividualShift import IndividualShift

shiftAPI.add_resource(IndividualShift, "/<string:uuid>")
