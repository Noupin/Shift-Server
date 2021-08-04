#pylint: disable=C0103, C0301
"""
The utility functions related to emails
"""
__author__ = "Noupin"

#Third Party Imports
import os
from typing import List
from flask_mail import Message, Mail


def sendEmail(mail: Mail, subject: str, recipients: List[str], msg: str, sender: str=os.environ.get("MAIL_USERNAME")):
    msg = Message(subject=subject,
                  sender=sender,
                  recipients=recipients,
                  body=msg)

    mail.send(msg)
