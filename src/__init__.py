#pylint: disable=C0103, C0301, R0903, E1101
"""
Creates the flask server
"""
__author__ = "Noupin"

#Third Party Imports
import flask
from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from flask_mongoengine import MongoEngine
from flask_bcrypt import Bcrypt
from flask_mail import Mail

#First Party Imports
from src.config import Config
from src.variables.globals import Globals
from src.utils.FlaskCelery import FlaskCelery
from src.utils.MJSONEncoder import MongoJSONEncoder


shiftGlobals = Globals()
cors = CORS()
login_manager = LoginManager()
db = MongoEngine()
bcrypt = Bcrypt()
mail = Mail()
celery = FlaskCelery()
print("Main:",celery)


def createApp(appName=__name__, configClass=Config, **kwargs) -> flask.app.Flask:
    """
    Creates the Shift Flask App and if given a config class the default config class is overridden.

    Args:
        appName (str): The name of the Flask applcation
        configClass (Config, optional): The configuration settings for the Flask app. Defaults to Config.
        **kwargs: The extra keyword arguments to apply to the init_celery funciton

    Returns:
        flask.app.Flask: The created Flask app.
    """

    app = Flask(appName, static_folder="static/build", static_url_path="/")
    app.json_encoder = MongoJSONEncoder
    app.config.from_object(configClass)
    app.config["SHIFT_GLOBALS"] = shiftGlobals


    cors.init_app(app)
    login_manager.init_app(app)
    db.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    celery.init_app(app)


    from src.main.routes import main
    from src.api.load.routes import loadBP
    from src.api.train.routes import trainBP
    from src.api.inference.routes import inferenceBP
    from src.api.users.routes import users


    app.register_blueprint(main)
    app.register_blueprint(loadBP, url_prefix="/api")
    app.register_blueprint(trainBP, url_prefix="/api")
    app.register_blueprint(inferenceBP, url_prefix="/api")
    app.register_blueprint(users, url_prefix='/api/users')

    return app
