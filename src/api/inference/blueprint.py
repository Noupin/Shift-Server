#pylint: disable=C0103, C0301
"""
Routes for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from flask import Blueprint

#First Party Imports
from src.api.inference.routes.Inference import Inference
from src.api.inference.routes.InferenceStatus import InferenceStatus


inferenceBP = Blueprint('inference', __name__)

inferenceBP.add_url_rule("/inference", view_func=Inference.as_view("inference"))
inferenceBP.add_url_rule("/inferenceStatus", view_func=InferenceStatus.as_view("inferenceStatus"))
