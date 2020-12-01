#pylint: disable=C0103, C0301
"""
Routes for the Shift webapp
"""
__author__ = "Noupin"

#Third Party Imports
from flask import Blueprint


main = Blueprint('main', __name__, static_folder="../static/build", static_url_path="/")


@main.route('/')
def index():
    return main.send_static_file('index.html')
