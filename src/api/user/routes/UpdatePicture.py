#pylint: disable=C0103, C0301
"""
Update Picture endpoint for the user part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
import os
from PIL import Image
from flask import current_app
from flask_restful import Resource
from werkzeug.utils import secure_filename
from flask_apispec.views import MethodResource
from werkzeug.datastructures import FileStorage
from flask_apispec import marshal_with, use_kwargs, doc
from flask_jwt_extended import current_user, jwt_required

#First Party Imports
from src.utils.MultiImage import MultiImage
from src.DataModels.MongoDB.User import User
from src.utils.validators import (validateFilename,
                                  validateFileRequest)
from src.variables.constants import IMAGE_PATH, AUTHORIZATION_TAG
from src.utils.files import generateUniqueFilename, getMediaType
from src.DataModels.Request.UpdatePictureRequest import (UpdatePictureRequest,
                                                         UpdatePictureRequestDescription)
from src.DataModels.Response.UpdatePictureResponse import (UpdatePictureResponse,
                                                           UpdatePictureResponseDescription)


class UpdatePicture(MethodResource, Resource):

    @use_kwargs(UpdatePictureRequest, location="files",
                description=UpdatePictureRequestDescription)
    @marshal_with(UpdatePictureResponse.Schema(),
                  description=UpdatePictureResponseDescription)
    @doc(description="""Changes the users profile picture to the uploaded picture.""", tags=["User"],
operationId="updatePicture", consumes=['multipart/form-data'], security=AUTHORIZATION_TAG)
    @jwt_required()
    def put(self, requestFile: FileStorage):
        if not validateFileRequest([requestFile]):
            return UpdatePictureResponse(msg="The request payload had no files")

        _, uuid = generateUniqueFilename()
        _, ext = requestFile.filename.split(".")
        filename = f"{uuid}.{ext}"

        if requestFile.filename == '':
            return UpdatePictureResponse(msg="The request had no selected file.")

        if requestFile and validateFilename(requestFile.filename) and getMediaType(requestFile.filename) == "image":
            image = MultiImage(Image.open(requestFile))
            image.resize(maxDim=1024, keepAR=True)
            image.compress()
            image.save(os.path.join(current_app.root_path, IMAGE_PATH, secure_filename(filename)))
        else:
            return UpdatePictureResponse(msg="File not valid.")

        user: User = User.objects(id=current_user.id).first()
        
        if user.mediaFilename.find("default") == -1:
            try:
                os.remove(os.path.join(current_app.root_path, IMAGE_PATH, user.mediaFilename))
            except FileNotFoundError:
                pass
        
        user.update(set__mediaFilename=filename)

        return UpdatePictureResponse(msg="Picture updated.")
