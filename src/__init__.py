#pylint: disable=C0103, C0301, R0903, E1101
"""
Creates the flaks server
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
from src.utils.MJSONEncoder import MongoJSONEncoder
from src.utils.ObjectIdConverter import ObjectIdConverter


shiftGlobals = Globals()
cors = CORS()
login_manager = LoginManager()
db = MongoEngine()
bcrypt = Bcrypt()
mail = Mail()


def createApp(configClass=Config) -> flask.app.Flask:
    app = Flask(__name__, static_folder="static/build", static_url_path="/")
    app.json_encoder = MongoJSONEncoder
    app.config.from_object(configClass)
    app.config["SHIFT_GLOBALS"] = shiftGlobals


    cors.init_app(app)
    login_manager.init_app(app)
    db.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)


    from src.main.routes import main
    from src.api.routes import api
    from src.api.users.routes import users


    app.register_blueprint(main)
    app.register_blueprint(api, url_prefix="/api")
    app.register_blueprint(users, url_prefix='/api/users')

    return app
