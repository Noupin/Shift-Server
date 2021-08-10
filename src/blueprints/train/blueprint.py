#pylint: disable=C0103, C0301
"""
Routes for the Train part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from flask import Blueprint
from flask_restful import Api

#First Party Imports
from src.constants import BLUEPRINT_NAMES


trainBP = Blueprint(BLUEPRINT_NAMES.get("train"), __name__)
trainAPI = Api(trainBP)

from src.blueprints.train.routes.Train import Train
from src.blueprints.train.routes.StopTrain import StopTrain
from src.blueprints.train.routes.TrainStatus import TrainStatus

trainAPI.add_resource(Train, "/train")
trainAPI.add_resource(TrainStatus, "/trainStatus")
trainAPI.add_resource(StopTrain, "/stopTraining")
