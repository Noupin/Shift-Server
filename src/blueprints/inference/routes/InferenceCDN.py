#pylint: disable=C0103, C0301
"""
Inference CDN endpoint for the Inference part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
import os
import mimetypes
from flask_restful import Resource
from flask import current_app, abort
from werkzeug.utils import secure_filename
from flask_apispec import doc, marshal_with
from flask_apispec.views import MethodResource

#First Party Imports
from src.constants import INFERENCE_IMAGE_PATH


class InferenceCDN(MethodResource, Resource):

    @marshal_with(None)
    @doc(description="""The CDN to get non trained Shifted images.""", tags=["Inference"],
operationId="inferenceCDN")
    def get(self, filename: str):
        secureFilename = secure_filename(filename)
        filepath = os.path.join(current_app.root_path, INFERENCE_IMAGE_PATH, secureFilename)
        
        try:
            file = open(filepath, 'rb')
            mimetype = mimetypes.MimeTypes().guess_type(secureFilename)[0]
        except FileNotFoundError:
            return abort(404)

        def stream_and_remove_file():
            yield from file
            file.close()
            os.remove(filepath)

        return current_app.response_class(
            stream_and_remove_file(),
            headers={'Content-Type': mimetype, 'filename': filename}
        )
