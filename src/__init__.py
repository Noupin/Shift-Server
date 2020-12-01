#pylint: disable=C0103, C0301, R0903, E1101
"""
Creates the flaks server
"""
__author__ = "Noupin"

#Third Party Imports
from flask import Flask
from flask_cors import CORS

#First Party Imports
from src.config import Config


PRIVATE_KEY = open('keys/jwt-key').read()
PUBLIC_KEY = open('keys/jwt-key.pub').read()


def createApp(configClass=Config):
    app = Flask(__name__, static_folder="static/build", static_url_path="/")
    CORS(app)
    app.config.from_object(configClass)

    from src.users.routes import users
    from src.main.routes import main
    from src.api.routes import api

    app.register_blueprint(users)
    app.register_blueprint(main)
    app.register_blueprint(api)

    return app
