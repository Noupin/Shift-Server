#pylint: disable=C0103, C0301
"""
Routes for the Subscription part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from flask import Blueprint
from flask_restful import Api

#First Party Imports
from src.variables.constants import BLUEPRINT_NAMES


subscriptionBP = Blueprint(BLUEPRINT_NAMES.get("user"), __name__)
subscriptionAPI = Api(subscriptionBP)

from src.api.subscription.routes.StripePublishableKey import StripePublishableKey

subscriptionAPI.add_resource(StripePublishableKey, "/stripe-publishable-key")
