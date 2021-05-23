#pylint: disable=C0103, C0301
"""
Image endpoint for the CDN part of the Shift API
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
from flask_apispec import marshal_with, use_kwargs

#First Party Imports
from src.variables.constants import IMAGE_PATH
from src.DataModels.Request.MediaDownloadRequest import (MediaDownloadRequest,
                                                         MediaDownloadRequestDescription)


class ImageDownload(MethodResource, Resource):

    #@use_kwargs(MediaDownloadRequest.Schema(), location='query',
    #            description=MediaDownloadRequestDescription)
    @marshal_with(None)
    @doc(description="""The image portion of the Shift CDN.""", tags=["CDN"],
operationId="getImageDownload")
    def get(self, filename: str='default.jpg', download: str='False') -> Response:
        asAttachment = json.loads(download.lower())

        return send_from_directory(os.path.join(current_app.root_path, IMAGE_PATH),
                                  filename=filename,
                                  as_attachment=asAttachment,
                                  mimetype="image",
                                  cache_timeout=0)
