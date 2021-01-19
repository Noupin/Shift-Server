#celery -A src.kel.celery worker --pool=solo --loglevel=info
#pylint: disable=C0103, C0301, R0903, E1101
"""
Creates the celery worker
"""
__author__ = "Noupin"

#Third Party Imports
import flask
from celery import Celery, Task

#First Party Imports
from src import createApp
from src.celeryApp import celery
from src.utils.celeryHelpers import init_celery


app = createApp()
init_celery(app, celery)
#cel = celery
