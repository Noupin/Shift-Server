#pylint: disable=C0103, C0301
"""
The Marshmallow Schema for a user
"""

from __future__ import annotations

__author__ = "Noupin"

#Third Party Imports
from typing import Union
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, fields

#First Party Imports
from src import db
from src.models.SQL.User import User
from FeryvOAuthUser import FeryvUserSchema
from src.models.SQL.FeryvUser import FeryvUser


class UserSchema(SQLAlchemyAutoSchema):
    feryvUser = fields.Nested(FeryvUserSchema, optional=True)
    class Meta:
        model = User
        sqla_session = db.session
        include_relationships = True
        load_instance = True
        exclude = ("feryvId",)


    @staticmethod
    def getUserByUsername(username: str) -> Union[UserSchema, dict]:
        try:
            feryvUser = FeryvUser.filter_by_username(username)
            user: User = User.query.filter_by(feryvId=feryvUser.get('id')).first()
            setattr(user, 'feryvUser', feryvUser)
            userSchema = UserSchema().dump(user)
            userObject = UserSchema().load(userSchema)

            return userObject
        except ValueError:
            return None


    @staticmethod
    def getUserById(id: int) -> Union[UserSchema, dict]:
        try:
            feryvUser = FeryvUser.filter_by_id(id)
            user: User = User.query.filter_by(feryvId=feryvUser.get('id')).first()
            setattr(user, 'feryvUser', feryvUser)
            userSchema = UserSchema().dump(user)
            userObject = UserSchema().load(userSchema)

            return userObject
        except ValueError:
            return None
