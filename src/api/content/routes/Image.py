#pylint: disable=C0103, C0301
"""
Image endpoint for the CDN part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
import os
import json
from flask import current_app
from flask_restful import Resource
from flask.wrappers import Response
from marshmallow import Schema, fields
from flask_apispec import marshal_with
from flask.helpers import send_from_directory
from flask_apispec.views import MethodResource

#First Party Imports
from src.variables.constants import IMAGE_PATH


class ImageResponse(Schema):
    image = fields.Field()

class Image(MethodResource, Resource):

    @marshal_with(ImageResponse)
    def get(self, filename: str='default.jpg', download: str='False') -> Response:
        """
        The image portion of the CDN.

        Returns:
            Response: The file requested.
        """

        asAttachment = json.loads(download.lower())

        return send_from_directory(os.path.join(current_app.root_path, IMAGE_PATH),
                                  filename=filename,
                                  as_attachment=asAttachment,
                                  mimetype="image",
                                  cache_timeout=0)
