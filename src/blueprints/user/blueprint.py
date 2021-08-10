#pylint: disable=C0103, C0301
"""
Routes for the Users part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from flask import Blueprint
from flask_restful import Api

#First Party Imports
from src.constants import BLUEPRINT_NAMES


userBP = Blueprint(BLUEPRINT_NAMES.get("user"), __name__)
userAPI = Api(userBP)

from src.blueprints.user.routes.UserShifts import UserShifts
from src.blueprints.user.routes.IndividualUser import IndividualUser

userAPI.add_resource(IndividualUser, "/<string:username>")
userAPI.add_resource(UserShifts, "/<string:username>/shifts")
