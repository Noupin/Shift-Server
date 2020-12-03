#pylint: disable=C0103, C0301
"""
Routes for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity


api = Blueprint('api', __name__)


@api.route("/train", methods=["POST"])
@jwt_required
def train():
    """
    Given training data Shift specializes a model for the training data. Yeilds
    more relaisitic results than just an inference though it takes longer. 

    Returns:
        Shifted Media: The media that has been shifted by the specialized model.
    """

    return {'msg': f"Training as {get_jwt_identity()}"}


@api.route("/inference", methods=["POST"])
@jwt_required
def inference():
    """
    Inferenceing based on a specialized pretrained model(PTM) where, the input is
    the face to be put on the media and inferenced with PTM. Alternativley inferencing
    with a given base video and shift face with a non specialized PTM.

    Returns:
        Shifted Media: The media that has been shifted by the pretrained model.
    """

    return {'msg': f"Inferencing as {get_jwt_identity()}"}


@api.route('/featured', methods=["POST", "GET"])
def featured():
    """
    Uses TCP to send the data of the two featured models.

    Returns:
        JSON: Contains the list of the featured models.
    """

    return {"data": ["Alpha + Beta\nBetter together", "Eta & Iota\nBetter Apart"]}


@api.route('/popular', methods=["POST", "GET"])
def popular():
    """
    Uses TCP to send the data of the top 10 most popular models.

    Returns:
        JSON: Contains the list of the popular models.
    """

    return {"data": ["Black Panther", 
                     "Tony Stark",
                     "Captain America",
                     "Thor",
                     "Captain Marvel",
                     "Spider-Man",
                     "Robert Pattinson",
                     "Jesse Eisenberg",
                     "Andrew Garfield",
                     "Eleven"]}


@api.route('/new', methods=["POST", "GET"])
def new():
    """
    Uses TCP to send the data of the 10 newest models.

    Returns:
        JSON: Contains the list of the new models.
    """

    return {"data": ["The Protagonist",
                     "Robert Pattinson",
                     "Timothy Chalamet",
                     "Tony Stark",
                     "Jimmy Falon",
                     "Black Panther",
                     "Andrew Garfield",
                     "Jesse Eisenberg",
                     "Black Panther",
                     "Chrisjen Ava Sarala"]}
