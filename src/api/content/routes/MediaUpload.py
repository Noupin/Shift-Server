#pylint: disable=C0103, C0301
"""
Media Upload endpoint for the CDN part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
import os
from flask import current_app
from werkzeug import Response
from flask_restful import Resource
from flask_apispec import marshal_with, doc
from flask.helpers import send_from_directory
from flask_apispec.views import MethodResource

#First Party Imports
from src.variables.constants import IMAGE_PATH


class MediaUpload(MethodResource, Resource):

    @marshal_with(None)
    @doc(description="""The image portion of the Shift CDN.""", tags=["CDN"],
operationId="image")
    def post(self, filename: str='default.jpg') -> Response:

        return send_from_directory(os.path.join(current_app.root_path, IMAGE_PATH),
                                  filename=filename,
                                  as_attachment=False,
                                  mimetype="image",
                                  cache_timeout=0)
