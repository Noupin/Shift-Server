#pylint: disable=C0103, C0301
"""
Routes for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
import os
from flask.helpers import send_from_directory
from flask import Blueprint, current_app


content = Blueprint('content', __name__)

@content.route("/image/<shiftUUID>", methods=["GET"])
def image(shiftUUID):
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

    return send_from_directory(os.path.join(current_app.root_path, "..", current_app.config["SHIFT_MODELS_FOLDER"], shiftUUID, 'tmp'),
                               filename=shiftedFile,
                               as_attachment=False,
                               mimetype='image/png',
                               cache_timeout=0)
