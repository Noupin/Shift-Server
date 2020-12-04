#pylint: disable=C0103, C0301
"""
Mongo ObjectID Converter
"""
__author__ = "https://stackoverflow.com/users/1196339/nackjicholson"

#Third Party Imports
from datetime import datetime, date
import isodate as iso
from bson import ObjectId
from flask.json import JSONEncoder
from werkzeug.routing import BaseConverter


class ObjectIdConverter(BaseConverter):
    def to_python(self, value):
        return ObjectId(value)

    def to_url(self, value):
        return str(value)