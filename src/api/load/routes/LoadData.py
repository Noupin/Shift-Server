#pylint: disable=C0103, C0301
"""
Load Data endpoint for the Load part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from typing import List
from flask_restful import Resource
from flask_apispec.views import MethodResource
from werkzeug.datastructures import FileStorage
from flask_login import current_user, login_required
from flask_apispec import marshal_with, use_kwargs, doc

#First Party Imports
from src.variables.constants import SECURITY_TAG
from src.utils.validators import (validateFilename,
                                  validateFileRequest)
from src.utils.files import generateUniqueFilename, saveFlaskFile
from src.DataModels.Request.LoadDataRequest import (LoadDataBodyRequest,
                                                    LoadDataBodyRequestDescription,
                                                    LoadDataHeaderRequest,
                                                    LoadDataHeaderRequestDescription)
from src.DataModels.Response.LoadDataResponse import (LoadDataResponse,
                                                      LoadResponseDescription)


class LoadData(MethodResource, Resource):
    decorators = [login_required]

    @use_kwargs(LoadDataBodyRequest, location="files",
                description=LoadDataBodyRequestDescription)
    @use_kwargs(LoadDataHeaderRequest.Schema(), location="headers",
                description=LoadDataHeaderRequestDescription)
    @marshal_with(LoadDataResponse.Schema(),
                  description=LoadResponseDescription)
    @doc(description="""Given training data Shift specializes a model for the training data. \
Yeilds more relaisitic results than just an inference though it takes longer.""", tags=["Load"],
operationId="loadData", consumes=['multipart/form-data'], security=SECURITY_TAG)
    def post(self, requestHeaders: LoadDataHeaderRequest, requestFiles: List[FileStorage]):
        if not validateFileRequest(requestFiles):
            return {'msg': "The request payload had no files"}

        try:
            requestData: List[str] = requestHeaders.trainingDataTypes[0].split(',')
        except ValueError:
            return {"msg": "Not all fields for the LoadRequest object were POSTed"}
        except TypeError:
            return {"msg": "Not all fields for the LoadRequest object were POSTed"}

        if len(requestData) != len(requestFiles):
            return {'msg': "The number of training files and training data types does not match"}

        _, shiftUUID = generateUniqueFilename()

        for count, _ in enumerate(requestFiles):
            data = requestFiles[count]

            if data.filename == '':
                return {'msg': "The request had no selected file"}

            if data and validateFilename(data.filename):
                saveFlaskFile(data, shiftUUID,requestData, count=count)
            else:
                return {'msg': 'File not valid'}

        return {'msg': f"Loaded data as {current_user.username}", "shiftUUID": shiftUUID}
