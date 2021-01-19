#celery -A src.run.celery worker --pool=solo -l info
#pylint: disable=C0103, C0301, R0903, E1101
"""
Creates the celery applciation
"""
__author__ = "Noupin"

#Third Party Imports
import celery as cel
from celery import Celery

#First Party Imports
from src.config import Config


def make_celery(appName=__name__) -> cel.app.base.Celery:
    """
    Makes a celery app

    Args:
        appName (str, optional): The name of the Celery applciation. Defaults to __name__.

    Returns:
        celery.app.base.Celery: The Celery applicaiton
    """

    return Celery(appName, backend=Config.CELERY_RESULT_BACKEND, broker=Config.CELERY_BROKER_URL)

celery = make_celery()
