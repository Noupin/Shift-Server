#pylint: disable=C0103, C0301
"""
Routes for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
import os
import json
from flask import Blueprint, current_app
from flask.helpers import send_from_directory

#First Party Imports
from src.variables.constants import IMAGE_PATH, VIDEO_PATH


contentBP = Blueprint('content', __name__)


@contentBP.route("/image/<string:filename>", methods=["GET"])
@contentBP.route("/image/<string:filename>/<string:download>", methods=["GET"])
def image(filename: str='default', download: str='False'):
    asAttachment = json.loads(download.lower())

    return send_from_directory(os.path.join(current_app.root_path, IMAGE_PATH),
                               filename=filename,
                               as_attachment=asAttachment,
                               mimetype=f"image",
                               cache_timeout=0)


@contentBP.route("/video/<string:filename>", methods=["GET"])
@contentBP.route("/video/<string:filename>/<string:download>", methods=["GET"])
def video(filename: str, download: str='False'):
    asAttachment = json.loads(download.lower())

    return send_from_directory(os.path.join(current_app.root_path, VIDEO_PATH),
                               filename=filename,
                               as_attachment=asAttachment,
                               mimetype='video/mp4',
                               cache_timeout=0)
