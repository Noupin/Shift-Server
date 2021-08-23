#pylint: disable=C0103, C0301
"""
The Marshmallow Schema for a user
"""

from __future__ import annotations

from marshmallow_dataclass import NoneType

__author__ = "Noupin"

#Third Party Imports
from typing import Union, Tuple
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


    @staticmethod
    def getUserByUsername(username: str) -> Tuple[Union[UserSchema, NoneType], User]:
        feryvUser = FeryvUser.filterByUsername(username)
        user: User = User.query.filter_by(id=feryvUser.id).first()

        if not user or not feryvUser:
            return None, None

        setattr(user, 'feryvUser', feryvUser)
        userSchema = UserSchema().dump(user)
        userObject = UserSchema().load(userSchema)

        return userObject, user


    @staticmethod
    def getUserById(id: int) -> Tuple[Union[UserSchema, dict], User]:
        feryvUser = FeryvUser.filterById(id)
        user: User = User.query.filter_by(id=feryvUser.id).first()

        if not user or not feryvUser:
            return None, None

        setattr(user, 'feryvUser', feryvUser)
        userSchema = UserSchema().dump(user)
        userObject = UserSchema().load(userSchema)

        return userObject, user


    def __repr__(self):
        return f"UserSchema(username='{self.feryvUser.username}', email='{self.feryvUser.email}', confirmed='{self.feryvUser.confirmed}')"


    def __str__(self):
        return f"UserSchema(username='{self.feryvUser.username}', email='{self.feryvUser.email}', confirmed='{self.feryvUser.confirmed}')"
