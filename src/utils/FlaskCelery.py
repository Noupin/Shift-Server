#celery -A src.kel.celery worker --pool=solo --loglevel=info
#pylint: disable=C0103, C0301, R0903, E1101
"""
Creates the celery worker
"""
__author__ = "Noupin"

#Third Party Imports
import flask
from flask import Flask
from celery import Celery


imports = ('src.api.inference.tasks',
           'src.api.train.tasks',)


class FlaskCelery(Celery):

    def __init__(self, *args, **kwargs):
        super(FlaskCelery, self).__init__(*args, **kwargs)

        self.app = Flask(__name__)
        if 'app' in kwargs:
            print(kwargs['app'].config.get("name"))
            self.init_app(kwargs['app'])

        self.patch_task()
        self.autodiscover_tasks(imports)


    def patch_task(self):
        TaskBase = self.Task
        _celery = self

        class ContextTask(TaskBase):
            abstract = True

            def __call__(self, *args, **kwargs):
                if flask.has_app_context():
                    return TaskBase.__call__(self, *args, **kwargs)
                else:
                    with _celery.app.app_context():
                        return TaskBase.__call__(self, *args, **kwargs)

        self.Task = ContextTask


    def init_app(self, app: flask.app.Flask):
        self.app = app
        self.config_from_object(app.config)
        self.patch_task()

celery = FlaskCelery()