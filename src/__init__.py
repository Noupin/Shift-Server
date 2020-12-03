#pylint: disable=C0103, C0301, R0903, E1101
"""
Creates the flaks server
"""
__author__ = "Noupin"

#Third Party Imports
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

#First Party Imports
from src.config import Config


cors = CORS()
jwt = JWTManager()


def createApp(configClass=Config):
    app = Flask(__name__, static_folder="static/build", static_url_path="/")
    app.config.from_object(configClass)

    cors.init_app(app)
    jwt.init_app(app)


    from src.main.routes import main
    from src.api.routes import api
    from src.api.users.routes import users


    app.register_blueprint(main)
    app.register_blueprint(api, url_prefix="/api")
    app.register_blueprint(users, url_prefix='/api/users')

    return app
