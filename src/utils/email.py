#pylint: disable=C0103, C0301
"""
The utility functions related to emails
"""
__author__ = "Noupin"

#Third Party Imports
import os
from flask_mail import Message, Mail


#First Party Imports
from src.DataModels.MongoDB.User import User
from src.variables.constants import FORGOT_PASSWORD_RESET_TOKEN_EXPIRE, FRONT_END_URL


def sendForgotPasswordEmail(mail: Mail, user: User):
    token = User.getResetToken(user, FORGOT_PASSWORD_RESET_TOKEN_EXPIRE)
    msg = Message(subject="Password Reset Request",
                  sender=os.environ.get("MAIL_USERNAME"),
                  recipients=[user.email])

    msg.body = f"""To reset your password visit the following link:

{FRONT_END_URL}/reset-password/{token}

If you did not make this request then please ignore this email.

- Feryv"""

    mail.send(msg)

def sendConfirmRegistrationEmail(mail: Mail, user: User, email: str):
    token = User.getConfirmationToken(user, FORGOT_PASSWORD_RESET_TOKEN_EXPIRE)
    msg = Message(subject="Confirm Email",
                  sender=os.environ.get("MAIL_USERNAME"),
                  recipients=[email])

    msg.body = f"""To confirm your email visit the following link:

{FRONT_END_URL}/confirm-email/{token}

If you did not make this request then please ignore this email.

- Feryv"""

    mail.send(msg)
