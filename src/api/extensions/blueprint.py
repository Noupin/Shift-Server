#pylint: disable=C0103, C0301
"""
Routes for the Shift webapp
"""
__author__ = "Noupin"

#Third Party Imports
from src.DataModels.Marshmallow.User import UserSchema
from flask import Blueprint
from flask_restful import Api
from typing import Dict, Union

#First Party Imports
from src import jwt
from src.DataModels.MongoDB.User import User
from src.variables.constants import BLUEPRINT_NAMES
from src.DataModels.MongoDB.TokenBlocklist import TokenBlocklist


extenstionBP = Blueprint(BLUEPRINT_NAMES.get("extension"), __name__)
extensionAPI = Api(extenstionBP)


@jwt.user_identity_loader
def user_identity_lookup(user: User) -> str:
    return user.id


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data: Dict[str, str]) -> Union[User, None]:
    identity = jwt_data["sub"]

    try:
        return User.objects(id=identity).first()
    except:
        return None


@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload: Dict[str, str]):
    jti = jwt_payload["jti"]
    token = TokenBlocklist.objects(jti=jti).first()

    return token is not None

@jwt.expired_token_loader
def my_expired_token_callback(_jwt_header, jwt_data):
    """
    The expired token endpoint for the Shift app.
    """

    return dict(msg="Your login has expired please login again."), 401


@jwt.invalid_token_loader
def my_invalid_token_callback(invalid_reason: str):
    """
    The invalid token endpoint for the Shift app.
    """

    return dict(msg=f"Your login is invalid beacause {invalid_reason}, please login again."), 401


@jwt.revoked_token_loader
def my_revoked_token_callback(_jwt_header, jwt_data):
    """
    The expired token endpoint for the Shift app.
    """

    return dict(msg="You have logged out please login."), 401


@jwt.additional_claims_loader
def add_claims_to_access_token(identity):
    """
    Adds the users object to the JWT access token claims

    Args:
        identity (str): The identy(pk) of the user

    Returns:
        dict: The user object
    """

    user = User.objects(id=identity.id).first()

    return dict(user=UserSchema().dump(user))
