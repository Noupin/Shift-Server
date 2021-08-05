#pylint: disable=C0103, C0301
"""
Confirmation Email endpoint for the Users part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
import stripe
from flask import current_app
from flask_restful import Resource
from flask_apispec import marshal_with, doc
from flask_apispec.views import MethodResource
from flask_jwt_extended import jwt_required, current_user

#First Party Imports
from src.variables.constants import AUTHORIZATION_TAG, FRONT_END_URL
from src.decorators.confirmationRequired import confirmationRequired
from src.DataModels.Response.StripeCreateCheckoutSessionResponse import (StripeCreateCheckoutSessionResponse,
                                                                         StripeCreateCheckoutSessionResponseDescription)


class StripeCreateCheckoutSession(MethodResource, Resource):

    @marshal_with(StripeCreateCheckoutSessionResponse.Schema(),
                  description=StripeCreateCheckoutSessionResponseDescription)
    @doc(description="""Sends the publishable stripe key.""",
tags=["Subscription"], operationId="createCheckoutSession", security=AUTHORIZATION_TAG)
    @jwt_required(locations=['headers'])
    @confirmationRequired
    def get(self) -> dict:
        stripe.api_key = current_app.config.get('STRIPE_SECRET_KEY')

        try:
            checkoutSession = stripe.checkout.Session.create(
                # you should get the user id here and pass it along as 'client_reference_id'
                #
                # this will allow you to associate the Stripe session with
                # the user saved in your database
                #
                # example: client_reference_id=user.id,
                client_reference_id=current_user.id,
                success_url=FRONT_END_URL + "/subscription/success?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=FRONT_END_URL + "/subscription/cancel",
                payment_method_types=["card"],
                mode="subscription",
                line_items=[
                    {
                        "price": current_app.config.get('STRIPE_PRICE_ID'),
                        "quantity": 1,
                    }
                ]
            )
            
            return StripeCreateCheckoutSessionResponse(sessionId=checkoutSession['id'])
        except:
            return StripeCreateCheckoutSessionResponse(), 403
