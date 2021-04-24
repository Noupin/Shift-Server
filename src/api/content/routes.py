#pylint: disable=C0103, C0301
"""
Routes for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
import os
import json
from flask.helpers import send_file, send_from_directory
from flask import Blueprint, current_app


content = Blueprint('content', __name__)


@content.route("/shiftImage/<string:shiftUUID>", methods=["GET"])
def shiftImage(shiftUUID):
    tmpFiles = os.listdir(os.path.join(current_app.config["SHIFT_MODELS_FOLDER"], shiftUUID, 'tmp'))

    fileIndex = -1
    for index, filename in enumerate(tmpFiles):
        if filename.find(shiftUUID) == -1:
            continue
        fileIndex = index
        break
        
    if fileIndex == -1:
        return {'msg': "Could not find the shifted image"}

    shiftedFile = tmpFiles[fileIndex]

    print(shiftedFile)
    return send_from_directory(os.path.join(current_app.root_path, "..", current_app.config["SHIFT_MODELS_FOLDER"], shiftUUID, 'tmp'),
                               filename=shiftedFile,
                               as_attachment=False,
                               mimetype='image/png',
                               cache_timeout=0)

@content.route("/image/<string:filename>", methods=["GET"])
@content.route("/image/<string:filename>/<string:download>", methods=["GET"])
def image(filename: str='default', download: str='False'):
    for file in os.listdir(os.path.join(current_app.root_path, "static", "images")):
        if file.split('.')[0] != filename:
            continue
        
        filename = file
        break
    
    asAttachment = json.loads(download.lower())

    return send_from_directory(os.path.join(current_app.root_path, "static", "images"),
                               filename=filename,
                               as_attachment=asAttachment,
                               mimetype=f"image/{filename.split('.')[-1].lower()}",
                               cache_timeout=0)

@content.route("/video/<string:filename>", methods=["GET"])
@content.route("/video/<string:filename>/<string:download>", methods=["GET"])
def video(filename: str, download: str='False'):
    for file in os.listdir(os.path.join(current_app.root_path, "static", "videos")):
        if file.split('.')[0] != filename:
            continue
        
        filename = file
        break

    asAttachment = json.loads(download.lower())

    return send_from_directory(os.path.join(current_app.root_path, "static", "videos"),
                               filename=filename,
                               as_attachment=asAttachment,
                               mimetype='video/mp4',
                               cache_timeout=0)
