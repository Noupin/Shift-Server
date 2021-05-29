#pylint: disable=C0103, C0301
"""
Routes for the Users part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from flask import Blueprint
from flask_restful import Api

#First Party Imports
from src.variables.constants import BLUEPRINT_NAMES


userBP = Blueprint(BLUEPRINT_NAMES.get("user"), __name__)
userAPI = Api(userBP)

from src.api.user.routes.Shifts import Shifts
from src.api.user.routes.Profile import Profile
from src.api.user.routes.UpdatePicture import UpdatePicture
from src.api.user.routes.IndividualUser import IndividualUser

userAPI.add_resource(Shifts, "/data/shifts")
userAPI.add_resource(Profile, "/data/profile")
userAPI.add_resource(UpdatePicture, "/data/updatePicture")
userAPI.add_resource(IndividualUser, "/<string:username>")
