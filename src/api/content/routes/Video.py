#pylint: disable=C0103, C0301
"""
Video endpoint for the CDN part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
import os
import json
from flask import current_app
from flask_restful import Resource
from flask.wrappers import Response
from flask.helpers import send_from_directory

#First Party Imports
from src.variables.constants import VIDEO_PATH


class Video(Resource):

    def get(self, filename: str='default.mp4', download: str='False') -> Response:
        """
        The video portion of the CDN.

        Returns:
            Response: The file requested.
        """

        asAttachment = json.loads(download.lower())

        return send_from_directory(os.path.join(current_app.root_path, VIDEO_PATH),
                                  filename=filename,
                                  as_attachment=asAttachment,
                                  mimetype='video',
                                  cache_timeout=0)
