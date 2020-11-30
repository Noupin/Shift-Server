#pylint: disable=C0103, C0301
"""
Tests the API requests
"""
__author__ = "Noupin"

#Third Party Imports
import os
import sys
import jwt
import json
import time
import pytest
import requests
import datetime

#Allow for Python. relative imports
dir_path = os.path.dirname(os.path.realpath(__file__))
parent_dir_path = os.path.abspath(os.path.join(dir_path, os.pardir))
sys.path.insert(0, parent_dir_path)

#First Party Imports
from ServerData import ServerData


loginURL = ServerData.loginURL
protectedURL = ServerData.protectedURL

myObj = {"username": "noah",
         "password": "123"}

jwtPrefix = "Bearer "
head = {"Authorization": jwtPrefix}

def test_JWTHeader():
    """
    Tests the header of the JWT.
    """

    getJWT = requests.post(loginURL, json=myObj)
    token = json.loads(getJWT.text)["jwt"]

    header = jwt.get_unverified_header(token)

    assert header['alg'] == 'RS256'
    assert header['typ'] == "JWT"

def test_JWTBody():
    """
    Tests the body of the JWT.
    """

    getJWT = requests.post(loginURL, json=myObj)
    token = json.loads(getJWT.text)["jwt"]

    payload = jwt.decode(token, verify=False)

    assert payload['username'] == myObj['username']
    assert payload['claims'] == ['Shift', 'Forge']

def test_validJWTSignature():
    """
    Test the validity of the signature of the JWT
    """

    getJWT = requests.post(loginURL, json=myObj)
    token = json.loads(getJWT.text)["jwt"]

    head['Authorization'] = jwtPrefix+token
    checkToken = requests.post(protectedURL, json=myObj, headers=head)

    response = json.loads(checkToken.text)

    assert response['username'] == myObj['username']
    assert response['claims'] == ['Shift', 'Forge']

def test_timedOutAuth():
    """
    Test the delcined Authorization after the exp has timed out.
    """

    getJWT = requests.post(loginURL, json=myObj)
    token = json.loads(getJWT.text)["jwt"]

    time.sleep(2)

    head['Authorization'] = jwtPrefix+token
    checkToken = requests.post(protectedURL, json=myObj, headers=head)

    response = json.loads(checkToken.text)

    assert response == {'message': 'Token has timed out.'}

def test_noTokenAuth():
    """
    Test the delcined Authorization with no token.
    """

    getJWT = requests.post(loginURL, json=myObj)
    token = json.loads(getJWT.text)["jwt"]

    head['Authorization'] = jwtPrefix[:-1]
    checkToken = requests.post(protectedURL, json=myObj, headers=head)

    response = json.loads(checkToken.text)

    assert response == {'message': 'Token missing.'}

def test_missingTokenAuth():
    """
    Test the delcined Authorization with a missing token.
    """

    getJWT = requests.post(loginURL, json=myObj)
    token = json.loads(getJWT.text)["jwt"]

    head['Authorization'] = jwtPrefix
    checkToken = requests.post(protectedURL, json=myObj, headers=head)

    response = json.loads(checkToken.text)

    assert response == {'message': 'Token empty.'}

def test_invalidSignatureTokenAuth():
    """
    Test the delcined Authorization with an invalid signature.
    """

    getJWT = requests.post(loginURL, json=myObj)
    token = json.loads(getJWT.text)["jwt"]

    head['Authorization'] = jwtPrefix+"notSignedRight"
    checkToken = requests.post(protectedURL, json=myObj, headers=head)

    response = json.loads(checkToken.text)

    assert response == {'message': 'Signature invalid.'}

def test_validTokenAuth():
    """
    Test the accepted Authorization.
    """

    getJWT = requests.post(loginURL, json=myObj)
    token = json.loads(getJWT.text)["jwt"]

    head['Authorization'] = jwtPrefix+token
    checkToken = requests.post(protectedURL, json=myObj, headers=head)

    response = json.loads(checkToken.text)

    assert response['username'] == myObj['username']
    assert response['claims'] == ['Shift', 'Forge']
