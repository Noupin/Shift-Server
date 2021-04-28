#pylint: disable=C0103, C0301
"""
Routes for the Users part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from flask import Blueprint

#First Party Imports
from src.api.users.routes.Login import Login
from src.api.users.routes.Logout import Logout
from src.api.users.routes.Shifts import Shifts
from src.api.users.routes.Profile import Profile
from src.api.users.routes.Register import Register
from src.api.users.routes.Authenticated import Authenticated


usersBP = Blueprint('users', __name__)

usersBP.add_url_rule("/login", view_func=Login.as_view("login"))
usersBP.add_url_rule("/logout", view_func=Logout.as_view("logout"))
usersBP.add_url_rule("/shifts", view_func=Shifts.as_view("shifts"))
usersBP.add_url_rule("/profile", view_func=Profile.as_view("profile"))
usersBP.add_url_rule("/register", view_func=Register.as_view("register"))
usersBP.add_url_rule("/authenticated", view_func=Authenticated.as_view("authenticated"))
