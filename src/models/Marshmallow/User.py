#pylint: disable=C0103, C0301
"""
The Marshmallow Schema for a user
"""
__author__ = "Noupin"

#Third Party Imports
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, fields

#First Party Imports
from src import db
from src.models.SQL.User import User
from FeryvOAuthUser import FeryvUserSchema


class UserSchema(SQLAlchemyAutoSchema):
    feryvUser = fields.Nested(FeryvUserSchema)
    class Meta:
        model = User
        sqla_session = db.session
        include_relationships = True
        load_instance = True
        exclude = ("feryvId",)
