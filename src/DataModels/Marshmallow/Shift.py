#pylint: disable=C0103, C0301
"""
The Marshmallow Schema for a shift
"""
__author__ = "Noupin"

#Third Party Imports
from marshmallow import fields
from marshmallow_mongoengine import ModelSchema

#First Party Imports
from src.DataModels.MongoDB.Shift import Shift
from src.DataModels.Marshmallow.User import UserSchema


class ShiftSchema(ModelSchema):
    class Meta:
        model = Shift
    author = fields.Nested(UserSchema, required=True)