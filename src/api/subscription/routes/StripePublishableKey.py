#pylint: disable=C0103, C0301
"""
Confirmation Email endpoint for the Users part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from flask import current_app
from flask_restful import Resource
from flask_apispec import marshal_with, doc
from flask_apispec.views import MethodResource

#First Party Imports
from src.DataModels.Response.StripePublishableKeyResponse import (StripePublishableKeyResponse,
                                                                  StripePublishableKeyResponseDescription)


class StripePublishableKey(MethodResource, Resource):

    @marshal_with(StripePublishableKeyResponse.Schema(),
                  description=StripePublishableKeyResponseDescription)
    @doc(description="""Sends the publishable stripe key.""",
tags=["Subscription"], operationId="getStripePublishableKey")
    def get(self) -> dict:

        return StripePublishableKeyResponse(publicKey=current_app.config.get('STRIPE_PUBLISHABLE_KEY'))
