#celery -A src.run.celery worker --pool=solo -l info
#pylint: disable=C0103, C0301, R0903, E1101
"""
Connects the flask app to the celery app
"""
__author__ = "Noupin"

#Third Party Imports
import flask
import celery
from celery import Celery

#First Party Imports
from src.config import Config


imports = ('src.api.inference.tasks',
           'src.api.train.tasks',)


def init_celery(app: flask.app.Flask, cel: celery.app.base.Celery):
    """
    Add flask app context to a celery app

    Args:
        app (flask.app.Flask): The flask app to connect with celery
        cel (celery.app.base.Celery): The celery app to update to work with app.
    """

    cel.conf.update(app.config)
    cel.autodiscover_tasks(imports)

    TaskBase = cel.Task

    class ContextTask(cel.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context() and app.test_request_context():
                return TaskBase.__call__(self, *args, **kwargs)

    cel.Task = ContextTask
