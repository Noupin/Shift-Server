#pylint: disable=C0103, C0301
"""
Routes for the Inference part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from flask import Blueprint
from flask_restful import Api

#First Party Imports
from src.constants import BLUEPRINT_NAMES


inferenceBP = Blueprint(BLUEPRINT_NAMES.get("inference"), __name__)
inferenceAPI = Api(inferenceBP)

from src.blueprints.inference.routes.Inference import Inference
from src.blueprints.inference.routes.InferenceCDN import InferenceCDN
from src.blueprints.inference.routes.InferenceStatus import InferenceStatus

inferenceAPI.add_resource(Inference, "/inference")
inferenceAPI.add_resource(InferenceStatus, "/inferenceStatus")
inferenceAPI.add_resource(InferenceCDN, "/inference/content/<string:filename>")
