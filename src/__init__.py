#pylint: disable=C0103, C0301, R0903, E1101
"""
Creates the flask server.
"""
__author__ = "Noupin"

#Third Party Imports
import flask
from flask import Flask
from celery import Celery
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_apispec.extension import FlaskApiSpec
from werkzeug.middleware.proxy_fix import ProxyFix
from sqlalchemy_utils import database_exists, create_database

#First Party Imports
from FeryvDB import FeryvDB
from src.config import Config
from src.constants import (BLUEPRINT_NAMES, CELERY_RESULT_BACKEND,
                           USER_AUTHORIZATION_SCHEME, AUTHORIZATION_SCHEME_NAME,
                           CSRF_REFRESH_SCHEME_NAME, USER_CSRF_REFRESH_SCHEME,
                           REFRESH_TOKEN_COOKIE_SCHEME_NAME, USER_REFRESH_TOKEN_COOKIE_SCHEME,
                           CELERY_BROKER_URL)


db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()
feryvDB = FeryvDB()
docs = FlaskApiSpec()


def initDatabase(uri: str):
    """
    Checks if the database for uri exists and if not makes the database.

    Args:
        uri (str): The uri of the database to check if is in existance.
    """    

    if not database_exists(uri):
        create_database(uri)


def initApp(appName=__name__, configClass: Config=Config) -> flask.app.Flask:
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
    
    initDatabase(configClass.SQLALCHEMY_DATABASE_URI)

    app = Flask(appName)
    app.config.from_object(configClass)


    db.init_app(app)
    jwt.init_app(app)
    docs.init_app(app)
    bcrypt.init_app(app)
    
    from src.models.SQL.User import User
    from src.models.SQL.Shift import Shift
    from src.models.SQL.TrainWorker import TrainWorker
    from src.models.SQL.ShiftCategory import ShiftCategory
    from src.models.SQL.InferenceWorker import InferenceWorker
    
    with app.app_context():
        db.create_all()
        feryvDB.init_db(db)

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


    from src.blueprints.load.blueprint import loadBP
    from src.blueprints.user.blueprint import userBP
    from src.blueprints.shift.blueprint import shiftBP
    from src.blueprints.train.blueprint import trainBP
    from src.blueprints.category.blueprint import categoryBP
    from src.blueprints.inference.blueprint import inferenceBP
    from src.blueprints.extension.blueprint import extenstionBP

    app.register_blueprint(loadBP, url_prefix="")
    app.register_blueprint(trainBP, url_prefix="")
    app.register_blueprint(inferenceBP, url_prefix="")
    app.register_blueprint(userBP, url_prefix='/user')
    app.register_blueprint(shiftBP, url_prefix='/shift') #Get user from querying the feryv database
    app.register_blueprint(categoryBP, url_prefix="/shift/category")

    return app


def addMiddleware(app: flask.app.Flask, middleware=ProxyFix, **kwargs):
    """
    Adds middleware to an already created flask app.

    Args:
        app (flask.app.Flask): The application to add middleware to.
        middleware (class): The middleware to be applied to the app. Defaults to ProxyFix.
        kwargs: The keyword arguments to pass to the middleware argument.

    Modifies:
        app (flask.app.Flask): The Flask app with middleware.
    """

    app.wsgi_app = middleware(app.wsgi_app, **kwargs)


def addAfterRequestFunction(app: flask.app.Flask, func):
    """
    Adds function to the after request functions of an already created flask app.

    Args:
        app (flask.app.Flask): The application to the after request function to.
        func (function): The func to be added to the after request.

    Modifies:
        app (flask.app.Flask): The Flask app with after app requests.
    """

    app.after_request(func)


def generateSwagger() -> FlaskApiSpec:
    """
    Generates all the swagger documentation for eeach endpoint.
    
    Returns:
        FlaskApiSpec: The updates docs to create yaml file.
    """

    from src.blueprints.load.blueprint import LoadData
    from src.blueprints.shift.blueprint import IndividualShift
    from src.blueprints.user.blueprint import IndividualUser, UserShifts
    from src.blueprints.train.blueprint import Train, TrainStatus, StopTrain
    from src.blueprints.inference.blueprint import Inference, InferenceCDN, InferenceStatus
    from src.blueprints.category.blueprint import ShiftCategory, NewShifts, PopularShifts, Categories

    docs.register(LoadData, blueprint=BLUEPRINT_NAMES.get("load"))

    docs.register(Train, blueprint=BLUEPRINT_NAMES.get("train"))
    docs.register(StopTrain, blueprint=BLUEPRINT_NAMES.get("train"))
    docs.register(TrainStatus, blueprint=BLUEPRINT_NAMES.get("train"))    

    docs.register(UserShifts, blueprint=BLUEPRINT_NAMES.get("user"))
    docs.register(IndividualUser, blueprint=BLUEPRINT_NAMES.get("user"))

    docs.register(Inference, blueprint=BLUEPRINT_NAMES.get("inference"))
    docs.register(InferenceCDN, blueprint=BLUEPRINT_NAMES.get("inference"))
    docs.register(InferenceStatus, blueprint=BLUEPRINT_NAMES.get("inference"))

    docs.register(NewShifts, blueprint=BLUEPRINT_NAMES.get("category"))
    docs.register(Categories, blueprint=BLUEPRINT_NAMES.get("category"))
    docs.register(PopularShifts, blueprint=BLUEPRINT_NAMES.get("category"))
    docs.register(ShiftCategory, blueprint=BLUEPRINT_NAMES.get("category"))

    docs.register(IndividualShift, blueprint=BLUEPRINT_NAMES.get("shift"))

    docs.spec.components.security_scheme(AUTHORIZATION_SCHEME_NAME, USER_AUTHORIZATION_SCHEME)
    docs.spec.components.security_scheme(REFRESH_TOKEN_COOKIE_SCHEME_NAME, USER_REFRESH_TOKEN_COOKIE_SCHEME)
    docs.spec.components.security_scheme(CSRF_REFRESH_SCHEME_NAME, USER_CSRF_REFRESH_SCHEME)

    return docs


def makeCelery(app: flask.app.Flask) -> Celery:
    celery = Celery(app.import_name,
                    backend=CELERY_RESULT_BACKEND,
                    broker=CELERY_BROKER_URL)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context() and app.test_request_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

    return celery
