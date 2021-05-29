#pylint: disable=C0103, C0301
"""
Routes for the CDN part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from flask import Blueprint
from flask_restful import Api

#First Party Imports
from src.variables.constants import BLUEPRINT_NAMES


contentBP = Blueprint(BLUEPRINT_NAMES.get('content'), __name__)
contentAPI = Api(contentBP)

from src.api.content.routes.Image import Image
from src.api.content.routes.Video import Video
from src.api.content.routes.MediaUpload import MediaUpload
from src.api.content.routes.ImageDownload import ImageDownload
from src.api.content.routes.VideoDownload import VideoDownload

contentAPI.add_resource(MediaUpload, "/media/upload")
contentAPI.add_resource(Image, "/image/<string:filename>")
contentAPI.add_resource(ImageDownload, "/image/<string:filename>/<string:download>", endpoint="imageBool")
contentAPI.add_resource(Video, "/video/<string:filename>")
contentAPI.add_resource(VideoDownload, "/video/<string:filename>/<string:download>", endpoint="videoBool")
