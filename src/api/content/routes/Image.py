#pylint: disable=C0103, C0301
"""
Image endpoint for the CDN part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
import os
import json
from flask import current_app
from flask.views import MethodView
from flask.wrappers import Response
from flask.helpers import send_from_directory

#First Party Imports
from src.variables.constants import IMAGE_PATH


class Image(MethodView):

    @staticmethod
    def get(filename: str='default', download: str='False') -> Response:
        """
        The image protion of the CDN.

        Returns:
            Response: The file requested.
        """

        asAttachment = json.loads(download.lower())

        return send_from_directory(os.path.join(current_app.root_path, IMAGE_PATH),
                                  filename=filename,
                                  as_attachment=asAttachment,
                                  mimetype="image",
                                  cache_timeout=0)
