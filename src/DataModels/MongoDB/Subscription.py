#pylint: disable=C0103, C0301
"""
The MongoDB data model for a Shift
"""
__author__ = "Noupin"

#Third Party Imports
from mongoengine import StringField
from src.config import FERYV_DB_ALIAS

#First Party Imports
from src import feryvDB


class Subscription(feryvDB.Document):
    subscriptionId = StringField(required=True)

    meta = {
        'db_alias': FERYV_DB_ALIAS
    }

    def __repr__(self) -> str:
        return f"StripeCustomer(subscriptionId='hidden')"
