#pylint: disable=C0103, C0301
"""
Routes for the CDN part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from flask import Blueprint

#First Party Imports
from src.api.content.routes.Image import Image
from src.api.content.routes.Video import Video


contentBP = Blueprint('content', __name__)

contentBP.add_url_rule("/image/<string:filename>", view_func=Image.as_view("image"))
contentBP.add_url_rule("/image/<string:filename>/<string:download>", view_func=Image.as_view("imageBool"))
contentBP.add_url_rule("/video/<string:filename>", view_func=Video.as_view("video"))
contentBP.add_url_rule("/video/<string:filename>/<string:download>", view_func=Video.as_view("videoBool"))
