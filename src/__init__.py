#pylint: disable=C0103, C0301, R0903, E1101
"""
Creates the flask server.
"""
__author__ = "Noupin"

#Third Party Imports
import flask
from flask import Flask
from celery import Celery
from flask_mail import Mail
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_mongoengine import MongoEngine
from flask_apispec.extension import FlaskApiSpec
from werkzeug.middleware.proxy_fix import ProxyFix

#First Party Imports
from src.config import Config
from src.utils.MJSONEncoder import MongoJSONEncoder
from src.variables.constants import (BLUEPRINT_NAMES, REFRESH_SCHEME_NAME, USER_REFRESH_SCHEME,
                                     USER_AUTHORIZATION_SCHEME, AUTHORIZATION_SCHEME_NAME,
                                     CSRF_REFRESH_SCHEME_NAME, USER_CSRF_REFRESH_SCHEME)


mail = Mail()
bcrypt = Bcrypt()
jwt = JWTManager()
docs = FlaskApiSpec()
shiftDB = MongoEngine()
feryvDB = MongoEngine()


def initApp(appName=__name__, configClass=Config) -> flask.app.Flask:
    """
    Creates the Shift Flask App and if given a config class the default config \
class is overridden.

    Args:
        appName (str): The name of the Flask applcation
        configClass (Config, optional): The configuration settings for the Flask app. \
Defaults to Config.

    Returns:
        flask.app.Flask: The created Flask app.
    """

    app = Flask(appName)
    app.json_encoder = MongoJSONEncoder
    app.config.from_object(configClass)


    jwt.init_app(app)
    mail.init_app(app)
    docs.init_app(app)
    bcrypt.init_app(app)
    shiftDB.init_app(app)

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


    from src.api.load.blueprint import loadBP
    from src.api.user.blueprint import userBP
    from src.api.shift.blueprint import shiftBP
    from src.api.train.blueprint import trainBP
    from src.api.content.blueprint import contentBP
    from src.api.category.blueprint import categoryBP
    from src.api.inference.blueprint import inferenceBP
    from src.api.extensions.blueprint import extenstionBP
    from src.api.authenticate.blueprint import authenticateBP

    app.register_blueprint(loadBP, url_prefix="/api")
    app.register_blueprint(trainBP, url_prefix="/api")
    app.register_blueprint(extenstionBP, url_prefix="")
    app.register_blueprint(inferenceBP, url_prefix="/api")
    app.register_blueprint(userBP, url_prefix='/api/user')
    app.register_blueprint(shiftBP, url_prefix='/api/shift')
    app.register_blueprint(contentBP, url_prefix='/api/content')
    app.register_blueprint(categoryBP, url_prefix="/api/shift/category")
    app.register_blueprint(authenticateBP, url_prefix='/api/authenticate')

    return app


def addMiddleware(app: flask.app.Flask, middleware=ProxyFix) -> flask.app.Flask:
    """
    Adds middleware to an already created flask app.

    Args:
        app (flask.app.Flask): The application to add middleware to.
        middleware (class): The middleware to be applied to the app. Defaults to ProxyFix.

    Returns:
        flask.app.Flask: The Flask app with middleware.
    """

    app.wsgi_app = middleware(app.wsgi_app)

    return app


def generateSwagger() -> FlaskApiSpec:
    """
    Generates all the swagger documentation for eeach endpoint.
    
    Returns:
        FlaskApiSpec: The updates docs to create yaml file.
    """

    from src.api.load.blueprint import LoadData
    from src.api.shift.blueprint import IndividualShift
    from src.api.train.blueprint import Train, TrainStatus, StopTrain
    from src.api.inference.blueprint import Inference, InferenceStatus
    from src.api.authenticate.blueprint import Register, Login, Logout, Refresh
    from src.api.content.blueprint import Image, Video, ImageDownload, VideoDownload
    from src.api.category.blueprint import ShiftCategory, NewShifts, PopularShifts, Categories
    from src.api.user.blueprint import UpdatePicture, IndividualUser, UserShifts, ChangePassword, ForgotPassword, ResetPassword

    docs.register(LoadData, blueprint=BLUEPRINT_NAMES.get("load"))

    docs.register(Train, blueprint=BLUEPRINT_NAMES.get("train"))
    docs.register(TrainStatus, blueprint=BLUEPRINT_NAMES.get("train"))
    docs.register(StopTrain, blueprint=BLUEPRINT_NAMES.get("train"))

    docs.register(Login, blueprint=BLUEPRINT_NAMES.get("authenticate"))
    docs.register(Logout, blueprint=BLUEPRINT_NAMES.get("authenticate"))
    docs.register(Refresh, blueprint=BLUEPRINT_NAMES.get("authenticate"))
    docs.register(Register, blueprint=BLUEPRINT_NAMES.get("authenticate"))

    docs.register(UserShifts, blueprint=BLUEPRINT_NAMES.get("user"))
    docs.register(ResetPassword, blueprint=BLUEPRINT_NAMES.get("user"))
    docs.register(UpdatePicture, blueprint=BLUEPRINT_NAMES.get("user"))
    docs.register(IndividualUser, blueprint=BLUEPRINT_NAMES.get("user"))
    docs.register(ChangePassword, blueprint=BLUEPRINT_NAMES.get("user"))
    docs.register(ForgotPassword, blueprint=BLUEPRINT_NAMES.get("user"))

    docs.register(Inference, blueprint=BLUEPRINT_NAMES.get("inference"))
    docs.register(InferenceStatus, blueprint=BLUEPRINT_NAMES.get("inference"))

    docs.register(Image, blueprint=BLUEPRINT_NAMES.get("content"))
    docs.register(Video, blueprint=BLUEPRINT_NAMES.get("content"))
    docs.register(ImageDownload, blueprint=BLUEPRINT_NAMES.get("content"), endpoint="imageBool")
    docs.register(VideoDownload, blueprint=BLUEPRINT_NAMES.get("content"), endpoint="videoBool")

    docs.register(NewShifts, blueprint=BLUEPRINT_NAMES.get("category"))
    docs.register(Categories, blueprint=BLUEPRINT_NAMES.get("category"))
    docs.register(PopularShifts, blueprint=BLUEPRINT_NAMES.get("category"))
    docs.register(ShiftCategory, blueprint=BLUEPRINT_NAMES.get("category"))

    docs.register(IndividualShift, blueprint=BLUEPRINT_NAMES.get("shift"))

    docs.spec.components.security_scheme(AUTHORIZATION_SCHEME_NAME, USER_AUTHORIZATION_SCHEME)
    docs.spec.components.security_scheme(REFRESH_SCHEME_NAME, USER_REFRESH_SCHEME)
    docs.spec.components.security_scheme(CSRF_REFRESH_SCHEME_NAME, USER_CSRF_REFRESH_SCHEME)

    return docs


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
