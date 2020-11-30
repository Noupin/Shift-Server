#pylint: disable=C0103, C0301
"""
Finds open port can creates a data server to pass between front-end and backend
"""
__author__ = "Noupin"

#Third Party Imports
import os
import sys
import json
import time
import requests

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

getJWT = requests.post(loginURL, json=myObj)
token = json.loads(getJWT.text)["jwt"]

#time.sleep(2)
head['Authorization'] = jwtPrefix+token
checkToken = requests.post(protectedURL, json=myObj, headers=head)
print(json.loads(checkToken.text))
