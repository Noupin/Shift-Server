#pylint: disable=C0103, C0301
"""
Routes for the Load part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from flask import Blueprint

#First Party Imports
from src.api.load.routes.LoadData import LoadData


loadBP = Blueprint('load', __name__)

loadBP.add_url_rule("/loadData", view_func=LoadData.as_view("loadData"))
