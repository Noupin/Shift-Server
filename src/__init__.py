#pylint: disable=C0103, C0301, R0903, E1101
"""
Creates the flask server
"""
__author__ = "Noupin"

#Third Party Imports
import flask
from flask import Flask
from celery import Celery
from flask_cors import CORS
from flask_login import LoginManager
from flask_mongoengine import MongoEngine
from flask_bcrypt import Bcrypt
from flask_mail import Mail

#First Party Imports
from src.config import Config
from src.utils.MJSONEncoder import MongoJSONEncoder


cors = CORS()
login_manager = LoginManager()
db = MongoEngine()
bcrypt = Bcrypt()
mail = Mail()


def initApp(appName=__name__, configClass=Config) -> flask.app.Flask:
    """
    Creates the Shift Flask App and if given a config class the default config class is overridden.

    Args:
        appName (str): The name of the Flask applcation
        configClass (Config, optional): The configuration settings for the Flask app. Defaults to Config.

    Returns:
        flask.app.Flask: The created Flask app.
    """

    app = Flask(appName, static_folder="static/build", static_url_path="/")
    app.json_encoder = MongoJSONEncoder
    app.config.from_object(configClass)


    cors.init_app(app)
    login_manager.init_app(app)
    db.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)

    return app


def createApp(app=None, appName=__name__, configClass=Config) -> flask.app.Flask:
    """
    Creates the Shift Flask App and if given a config class the default config class is overridden.

    Args:
        app (flask.app.Flask): The application to update the blueprints of
        appName (str): The name of the Flask applcation
        configClass (Config, optional): The configuration settings for the Flask app. Defaults to Config.

    Returns:
        flask.app.Flask: The created Flask app.
    """

    if not app:
        app = initApp(appName, configClass)


    from src.main.routes import main
    from src.api.load.blueprint import loadBP
    from src.api.train.routes import trainBP
    from src.api.inference.blueprint import inferenceBP
    from src.api.users.blueprint import usersBP
    from src.api.content.blueprint import contentBP


    app.register_blueprint(main)
    app.register_blueprint(loadBP, url_prefix="/api")
    app.register_blueprint(trainBP, url_prefix="/api")
    app.register_blueprint(inferenceBP, url_prefix="/api")
    app.register_blueprint(usersBP, url_prefix='/api/users')
    app.register_blueprint(contentBP, url_prefix='/api/content')

    return app


def makeCelery(app: flask.app.Flask):
    celery = Celery(app.import_name,
                    backend=app.config['CELERY_RESULT_BACKEND'],
                    broker=app.config['CELERY_BROKER_URL'])

    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context() and app.test_request_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

    return celery
