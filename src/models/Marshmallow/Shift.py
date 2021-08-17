#pylint: disable=C0103, C0301
"""
The Marshmallow Schema for a shift
"""
__author__ = "Noupin"

#Third Party Imports
from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

#First Party Imports
from src import db
from src.models.SQL.Shift import Shift
from src.models.Marshmallow.User import UserSchema


class ShiftSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Shift
        sqla_session = db.session
        include_relationships = True
        load_instance = True

    author = fields.Nested(UserSchema, required=True)
