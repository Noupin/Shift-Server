#pylint: disable=C0103, C0301
"""
Mongo ObjectID Converter
"""
__author__ = "https://stackoverflow.com/users/1196339/nackjicholson"

#Third Party Imports
from bson import ObjectId
from werkzeug.routing import BaseConverter


class ObjectIdConverter(BaseConverter):
    """
    Converts the ObjectId of the MongoDB BSON to JSON

    Args:
        BaseConverter
    """

    def to_python(self, value):
        return ObjectId(value)

    def to_url(self, value):
        return str(value)
