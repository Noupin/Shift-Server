#celery -A hello worker --pool=solo -l info
#pylint: disable=C0103, C0301, R0903, E1101
"""
Creates the flaks server
"""
__author__ = "Noupin"

#Third Party Imports
from celery import Celery

#First Party Imports
from src import Config


celery = Celery("Shift")
celery.config_from_object(Config)
