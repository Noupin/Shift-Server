#pylint: disable=C0103, C0301
"""
The Marshmallow Schema for a user
"""
__author__ = "Noupin"

#Third Party Imports
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

#First Party Imports
from src.models.SQL.User import User


class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_relationships = True
        load_instance = True
