#pylint: disable=C0103, C0301
"""
The MongoDB data model for a Shift
"""
__author__ = "Noupin"

#Third Party Imports
from src.config import SHIFT_DB_ALIAS
from mongoengine import StringField, ReferenceField

#First Party Imports
from src import shiftDB
from src.DataModels.MongoDB.User import User


class StripeCustomer(shiftDB.Document):
    userID = ReferenceField(User, required=True)
    stripeCustomerId = StringField(required=True)
    stripeSubscriptionId = StringField(required=True)

    meta = {
        'db_alias': SHIFT_DB_ALIAS
    }

    def __repr__(self) -> str:
        return f"StripeCustomer('{self.stripeCustomerId}')"
