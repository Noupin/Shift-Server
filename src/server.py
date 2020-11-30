#pylint: disable=C0103, C0301
"""
Finds open port can creates a data server to pass between front-end and
backend.
"""
__author__ = "Noupin"

#Third Party Imports
import os
import sys
import jwt
import flask
import datetime
import functools
import time


#First Party Imports
from ServerData import ServerData


#Port serving variables
portOpen = False
port = ServerData.port

#Create app
app = flask.Flask(__name__)

private_key = open('keys/jwt-key').read()
public_key = open('keys/jwt-key.pub').read()

def checkToken(f):
    """
    Checks the validity and expiration of the JWT
    """

    @functools.wraps(f)
    def decorated(*args, **kwargs):
        authorization = flask.request.headers['Authorization'].split(' ')

        if len(authorization) <= 1:
            return flask.jsonify({'message': 'Token missing.'}), 403

        token = authorization[1]

        if len(token) == 0:
            return flask.jsonify({'message': 'Token empty.'}), 403
        
        try: 
            data = jwt.decode(token, public_key, algorithms="RS256")
        except jwt.ExpiredSignatureError:
            return flask.jsonify({'message': 'Token has timed out.'}), 403
        except:
            return flask.jsonify({'message': 'Signature invalid.'}), 403

        return f(*args, **kwargs)

    return decorated


@app.route('/time')
def gerCurrentTime():
    return {"time", time.time()}

@app.route('/login', methods=["POST"])
def login():
    """
    The login for the user and distributes the JWT.

    Returns:
        JSON: A JWT token for future authorization.
    """

    data = flask.request.get_json()

    if data['username'] and data['password']:
        token = jwt.encode({'username' : data['username'],
                            'claims': ['Shift', 'Forge'],
                            'exp' : (datetime.datetime.utcnow()+datetime.timedelta(seconds=1))},
                           private_key,
                           algorithm='RS256').decode('utf-8')

        return flask.jsonify({'jwt' : token})
    
    return "Login Invalid.", 403

@app.route("/train", methods=["POST"])
@checkToken
def train():
    """
    Given training data Shift specializes a model for the training data. Yeilds
    more relaisitic results than just an inference though it takes longer. 

    Returns:
        Shifted Media: The media that has been shifted by the specialized model.
    """

    authorization = flask.request.headers['Authorization'].split(' ')
    token = authorization[1]
    data = jwt.decode(token, public_key, algorithms="RS256")

    return data

@app.route("/inference", methods=["POST"])
@checkToken
def inference():
    """
    Inferenceing based on a specialized pretrained model(PTM) where, the input is
    the face to be put on the media and inferenced with PTM. Alternativley inferencing
    with a given base video and shift face with a non specialized PTM.

    Returns:
        Shifted Media: The media that has been shifted by the pretrained model.
    """

    authorization = flask.request.headers['Authorization'].split(' ')
    token = authorization[1]
    data = jwt.decode(token, public_key, algorithms="RS256")

    return data

@app.route('/featured', methods=["POST", "GET"])
def featured():
    """
    Uses TCP to send the data of the two featured models.

    Returns:
        JSON: Contains the list of the featured models.
    """

    return flask.jsonify({"data": ["Alpha + Beta\nBetter together", "Eta & Iota\nBetter Apart"]})

@app.route('/popular', methods=["POST", "GET"])
def popular():
    """
    Uses TCP to send the data of the top 10 most popular models.

    Returns:
        JSON: Contains the list of the popular models.
    """

    return flask.jsonify({"data": ["Black Panther", 
                                   "Tony Stark",
                                   "Captain America",
                                   "Thor",
                                   "Captain Marvel",
                                   "Spider-Man",
                                   "Robert Pattinson",
                                   "Jesse Eisenberg",
                                   "Andrew Garfield",
                                   "Eleven"]})

@app.route('/new', methods=["POST", "GET"])
def new():
    """
    Uses TCP to send the data of the 10 newest models.

    Returns:
        JSON: Contains the list of the new models.
    """

    return flask.jsonify({"data": ["The Protagonist",
                                   "Robert Pattinson",
                                   "Timothy Chalamet",
                                   "Tony Stark",
                                   "Jimmy Falon",
                                   "Black Panther",
                                   "Andrew Garfield",
                                   "Jesse Eisenberg",
                                   "Black Panther",
                                   "Chrisjen Ava Sarala"]})


#Run server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port, debug=True)
