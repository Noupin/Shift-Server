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
from flask_mail import Mail
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mongoengine import MongoEngine
from flask_apispec.extension import FlaskApiSpec

#First Party Imports
from src.config import Config
from src.utils.MJSONEncoder import MongoJSONEncoder
from src.variables.constants import BLUEPRINT_NAMES


cors = CORS()
login_manager = LoginManager()
db = MongoEngine()
bcrypt = Bcrypt()
mail = Mail()
docs = FlaskApiSpec()


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
    docs.init_app(app)

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
    from src.api.train.blueprint import trainBP
    from src.api.users.blueprint import usersBP
    from src.api.content.blueprint import contentBP
    from src.api.inference.blueprint import inferenceBP

    app.register_blueprint(main)
    app.register_blueprint(loadBP, url_prefix="/api")
    app.register_blueprint(trainBP, url_prefix="/api")
    app.register_blueprint(inferenceBP, url_prefix="/api")
    app.register_blueprint(usersBP, url_prefix='/api/users')
    app.register_blueprint(contentBP, url_prefix='/api/content')

    return app


def generateSwagger():
    """
    Generates all the swagger documentation for eeach endpoint.
    """

    from src.api.load.blueprint import LoadData
    from src.api.train.blueprint import Train, TrainStatus, StopTrain
    from src.api.users.blueprint import Register, Authenticated, Login, Logout, Profile, UserShifts
    from src.api.content.blueprint import Image, Video
    from src.api.inference.blueprint import Inference, InferenceStatus
    
    docs.register(LoadData, blueprint=BLUEPRINT_NAMES.get("load"))

    docs.register(Train, blueprint=BLUEPRINT_NAMES.get("train"))
    docs.register(TrainStatus, blueprint=BLUEPRINT_NAMES.get("train"))
    docs.register(StopTrain, blueprint=BLUEPRINT_NAMES.get("train"))

    docs.register(Register, blueprint=BLUEPRINT_NAMES.get("users"))
    docs.register(Authenticated, blueprint=BLUEPRINT_NAMES.get("users"))
    docs.register(Login, blueprint=BLUEPRINT_NAMES.get("users"))
    docs.register(Logout, blueprint=BLUEPRINT_NAMES.get("users"))
    docs.register(Profile, blueprint=BLUEPRINT_NAMES.get("users"))
    docs.register(UserShifts, blueprint=BLUEPRINT_NAMES.get("users"))

    docs.register(Inference, blueprint=BLUEPRINT_NAMES.get("inference"))
    docs.register(InferenceStatus, blueprint=BLUEPRINT_NAMES.get("inference"))
    
    docs.register(Image, blueprint=BLUEPRINT_NAMES.get("content"))
    docs.register(Image, blueprint=BLUEPRINT_NAMES.get("content"), endpoint="imageBool")
    docs.register(Video, blueprint=BLUEPRINT_NAMES.get("content"))
    docs.register(Video, blueprint=BLUEPRINT_NAMES.get("content"), endpoint="videoBool")


def makeCelery(app: flask.app.Flask) -> Celery:
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
