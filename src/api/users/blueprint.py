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


usersBP = Blueprint(BLUEPRINT_NAMES.get("users"), __name__)
usersAPI = Api(usersBP)

from src.api.users.routes.Login import Login
from src.api.users.routes.Logout import Logout
from src.api.users.routes.Profile import Profile
from src.api.users.routes.Register import Register
from src.api.users.routes.UserShifts import UserShifts
from src.api.users.routes.Authenticated import Authenticated

usersAPI.add_resource(Login, "/login")
usersAPI.add_resource(Logout, "/logout")
usersAPI.add_resource(Profile, "/profile")
usersAPI.add_resource(Register, "/register")
usersAPI.add_resource(UserShifts, "/userShifts")
usersAPI.add_resource(Authenticated, "/authenticated")
