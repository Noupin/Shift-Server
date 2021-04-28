#pylint: disable=C0103, C0301
"""
Routes for the Train part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from flask import Blueprint

#First Party Imports
from src.api.train.routes.Train import Train
from src.api.train.routes.TrainStatus import TrainStatus
from src.api.train.routes.StopTrain import StopTrain


trainBP = Blueprint('train', __name__)

trainBP.add_url_rule("/train", view_func=Train.as_view("train"))
trainBP.add_url_rule("/trainStatus", view_func=TrainStatus.as_view("trainStatus"))
trainBP.add_url_rule("/stopTraining", view_func=StopTrain.as_view("stopTrain"))
