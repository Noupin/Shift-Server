#pylint: disable=C0103, C0301
"""
Routes for the Train part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from flask import Blueprint
from flask_restful import Api

#First Party Imports
from src.api.train.routes.Train import Train
from src.variables.constants import BLUEPRINT_NAMES
from src.api.train.routes.StopTrain import StopTrain
from src.api.train.routes.TrainStatus import TrainStatus


trainBP = Blueprint(BLUEPRINT_NAMES.get("train"), __name__)
trainAPI = Api(trainBP)

trainAPI.add_resource(Train, "/train")
trainAPI.add_resource(TrainStatus, "/trainStatus")
trainAPI.add_resource(StopTrain, "/stopTraining")
