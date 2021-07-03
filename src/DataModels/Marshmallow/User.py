#pylint: disable=C0103, C0301
"""
The Marshmallow Schema for a user
"""
__author__ = "Noupin"

#Third Party Imports
from marshmallow.decorators import post_dump
import marshmallow_mongoengine as ma

#First Party Imports
from src.DataModels.MongoDB.User import User


class UserSchema(ma.ModelSchema):
    class Meta:
        model = User
        exclude = ("password", "passwordSalt")    

