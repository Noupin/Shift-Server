#pylint: disable=C0103, C0301
"""
Routes for the Authenticate part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from flask import Blueprint
from flask_restful import Api

#First Party Imports
from src.variables.constants import BLUEPRINT_NAMES


authenticateBP = Blueprint(BLUEPRINT_NAMES.get("authenticate"), __name__)
authenticateAPI = Api(authenticateBP)

from src.api.authenticate.routes.Login import Login
from src.api.authenticate.routes.Logout import Logout
from src.api.authenticate.routes.Refresh import Refresh
from src.api.authenticate.routes.Register import Register
from src.api.authenticate.routes.ConfirmEmail import ConfirmEmail
from src.api.authenticate.routes.ResendConfirmEmail import ResendConfirmEmail

authenticateAPI.add_resource(Login, "/login")
authenticateAPI.add_resource(Logout, "/logout")
authenticateAPI.add_resource(Refresh, "/refresh")
authenticateAPI.add_resource(Register, "/register")
authenticateAPI.add_resource(ResendConfirmEmail, "/resend-confirm-email")
authenticateAPI.add_resource(ConfirmEmail, "/confirm-email/<string:token>")
