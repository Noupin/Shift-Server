#pylint: disable=C0103, C0301
"""
Handles extensions for the Feryv OAuth API
"""
__author__ = "Noupin"

#Third Party Imports
from flask import Blueprint
from sqlalchemy import text
from flask_restful import Api
from typing import Dict, Union

#First Party Imports
from src import jwt, db
from src.models.SQL.User import User
from src.constants import BLUEPRINT_NAMES
from src.models.Marshmallow.User import UserSchema


extenstionBP = Blueprint(BLUEPRINT_NAMES.get("extension"), __name__)
extensionAPI = Api(extenstionBP)


@jwt.user_identity_loader
def user_identity_lookup(user) -> str:
    return user.id


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data: Dict[str, str]) -> Union[User, None]:
    identity = jwt_data["sub"]

    try:
        return UserSchema.getUserById(identity)
    except:
        return None


@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload: Dict[str, str]):
    jti = jwt_payload["jti"]
    token = db.get_engine(bind='feryvDB').execute(text('select * from "tokenblocklist" where jti = :jti'),
                                                  {'jti': jti}).first()

    return token is not None


@jwt.expired_token_loader
def my_expired_token_callback(_jwt_header, jwt_data):
    """
    The expired token endpoint for the Feryv OAuth app.
    """

    return dict(msg="Your login has expired please login again."), 401


@jwt.invalid_token_loader
def my_invalid_token_callback(invalid_reason: str):
    """
    The invalid token endpoint for the Feryv OAuth app.
    """

    return dict(msg=f"Your login is invalid beacause {invalid_reason}, please login again."), 401


@jwt.revoked_token_loader
def my_revoked_token_callback(_jwt_header, jwt_data):
    """
    The expired token endpoint for the Feryv OAuth app.
    """

    return dict(msg="You have logged out please login."), 401


@jwt.token_verification_loader
def createUserAfterVeification(jwt_header, jwt_data: Dict[str, str]):
    verified = True

    if not jwt_data.get('user'):
        return verified
    if not jwt_data.get('user').get('id'):
        return verified
    if User.query.filter_by(id=jwt_data.get('user').get('id')).first():
        return verified

    user = User(id=jwt_data.get('user').get('id'))
    db.session.add(user)
    db.session.commit()

    return verified
