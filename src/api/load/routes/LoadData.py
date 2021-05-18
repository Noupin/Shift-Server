#pylint: disable=C0103, C0301
"""
Load Data endpoint for the Load part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
import json
from typing import List
from flask import request
from flask_restful import Resource
from flask_apispec.annotations import doc
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, use_kwargs
from flask_login import current_user, login_required

#First Party Imports
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

    #@use_kwargs(LoadDataBodyRequest, location="files",
    #            description=LoadDataBodyRequestDescription)
    @use_kwargs(LoadDataHeaderRequest.Schema(), location="headers",
                description=LoadDataHeaderRequestDescription)
    @marshal_with(LoadDataResponse.Schema(),
                  description=LoadResponseDescription)
    @doc(description="""Given training data Shift specializes a model for the training data. \
Yeilds more relaisitic results than just an inference though it takes longer.""", tags=["Load"],
operationId="loadData", consumes=['multipart/form-data'])
    def post(self, requestHeaders: LoadDataHeaderRequest):# **kwargs):
        if not validateFileRequest(request.files):
            return {'msg': "The request payload had no file"}

        try:
            requestData: List[str] = json.loads(requestHeaders.trainingDataTypes[0])
        except ValueError:
            return {"msg": "Not all fields for the LoadRequest object were POSTed"}
        except TypeError:
            return {"msg": "Not all fields for the TrainRequest object were POSTed"}

        if len(requestData) != len(request.files):
            return {'msg': "The number of training files and training data types does not match"}

        shiftUUID, _ = generateUniqueFilename()
        shiftUUID = str(shiftUUID)

        for count, _ in enumerate(request.files):
            data = request.files[_]

            if data.filename == '':
                return {'msg': "The request had no selected file"}

            if data and validateFilename(data.filename):
                saveFlaskFile(data, shiftUUID,requestData, count=count)
            else:
                return {'msg': 'File not valid'}

        return {'msg': f"Loaded data as {current_user.username}", "shiftUUID": shiftUUID}
