#pylint: disable=C0103, C0301
"""
Mongo JSON Encoder
"""
__author__ = "https://stackoverflow.com/users/1196339/nackjicholson"

#Third Party Imports
from datetime import datetime, date
import isodate as iso
from bson import ObjectId
from flask.json import JSONEncoder


class MongoJSONEncoder(JSONEncoder):
    """
    Working JSON/BSON encoder

    Args:
        JSONEncoder
    """

    def default(self, o):
        if isinstance(o, (datetime, date)):
            return iso.datetime_isoformat(o)
        if isinstance(o, ObjectId):
            return str(o)
        else:
            return super().default(o)
