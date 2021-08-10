#pylint: disable=C0103, C0301
"""
Routes for the Load part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from flask import Blueprint
from flask_restful import Api

#First Party Imports
from src.constants import BLUEPRINT_NAMES


loadBP = Blueprint(BLUEPRINT_NAMES.get("load"), __name__)
loadAPI = Api(loadBP)

from src.blueprints.load.routes.LoadData import LoadData

loadAPI.add_resource(LoadData, "/loadData")
