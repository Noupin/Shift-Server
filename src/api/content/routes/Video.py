#pylint: disable=C0103, C0301
"""
Video endpoint for the CDN part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
import os
import json
from flask import current_app
from werkzeug import Response
from flask_restful import Resource
from flask_apispec.annotations import doc
from flask.helpers import send_from_directory
from flask_apispec.views import MethodResource

#First Party Imports
from src.variables.constants import VIDEO_PATH


class Video(MethodResource, Resource):

    @doc(description="""The video portion of the Shift CDN.""", tags=["CDN"],
operationId="video")
    def get(self, filename: str='default.mp4', download: str='False') -> Response:
        asAttachment = json.loads(download.lower())

        return send_from_directory(os.path.join(current_app.root_path, VIDEO_PATH),
                                  filename=filename,
                                  as_attachment=asAttachment,
                                  mimetype='video/mp4',
                                  cache_timeout=0)
