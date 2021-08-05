#pylint: disable=C0103, C0301
"""
Confirmation Email endpoint for the Users part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from flask_restful import Resource
from flask_apispec import marshal_with, doc
from flask_apispec.views import MethodResource

#First Party Imports



class StripePublishableKey(MethodResource, Resource):

    @marshal_with(VerifyEmailChangeResponse.Schema(),
                  description=VerifyEmailChangeResponseDescription)
    @doc(description="""Sends the publishable stripe key.""",
tags=["Subscription"], operationId="getStripePublishableKey")
    def get(self, token) -> dict:
        nextEmail, user = User.verifyChangeEmailToken(token)
        
        if user is None:
            return VerifyEmailChangeResponse(msg="The token has expired or is invalid.")
        
        sendEmail(mail, subject=VERIFY_EMAIL_CHANGE_SUBJECT, recipients=[nextEmail],
                  msg=confirmEmailChangeMessageTemplate(user.getChangeEmailToken(nextEmail)))

        return VerifyEmailChangeResponse(msg=f"You have verified your email to be changed. Please confirm your new email.",
                                         confirmed=True, nextEmail=nextEmail)
