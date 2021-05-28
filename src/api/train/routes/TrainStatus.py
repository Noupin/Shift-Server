#pylint: disable=C0103, C0301
"""
Train Status endpoint for the Train part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
import mongoengine
from flask import request
from flask_restful import Resource
from celery.result import AsyncResult
from flask_login import login_required
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, use_kwargs, doc

#First Party Imports
from src.run import celery
from src.variables.constants import SECURITY_TAG
from src.utils.validators import validateBaseTrainRequest
from src.DataModels.MongoDB.TrainWorker import TrainWorker
from src.DataModels.DataModelAdapter import DataModelAdapter
from src.DataModels.Request.TrainRequest import (TrainRequest,
                                                 TrainRequestDescription)
from src.DataModels.Response.TrainStatusResponse import (TrainStatusResponse,
                                                         TrainStatusResponseDescription)


class TrainStatus(MethodResource, Resource):
    decorators = [login_required]

    @use_kwargs(TrainRequest.Schema(),
                description=TrainRequestDescription)
    @marshal_with(TrainStatusResponse.Schema(),
                  description=TrainStatusResponseDescription)
    @doc(description="""The status of of the current training task if called while training \
the task will switch to give an update image. After a certain amount of time the training \
will be completed automatically to allow for multiple users to train.""", tags=["Train"],
operationId="trainStatus", security=SECURITY_TAG)
    def post(self, requestData: TrainRequest) -> dict:
        requestError = validateBaseTrainRequest(request)
        if isinstance(requestError, dict):
            return requestError

        requestData = DataModelAdapter(requestData)

        try:
            worker: TrainWorker = TrainWorker.objects.get(shiftUUID=requestData.getModel().shiftUUID)
        except Exception as e:
            return {"msg": "That training worker does not exist"}

        job = AsyncResult(id=worker.workerID, backend=celery._get_backend())

        try:
            status = job.status

            if status == "PENDING":
                worker.update(set__inferencing=True)
                worker.reload()

                imagesUpdated = worker.imagesUpdated
                while not imagesUpdated:
                    worker.reload()
                    imagesUpdated = worker.imagesUpdated

                if len(worker.exhibitImages) > 0 and worker.imagesUpdated:
                    worker.update(set__imagesUpdated=False)
                    worker.reload()

                    return {'msg': f"Update for current shift", 'exhibit': worker.exhibitImages}
                
            elif status == "SUCCESS":
                worker.delete()

                return {'msg': "Training stopped", 'stopped': True}
            elif status == "FAILURE":
                worker.delete()

                return {'msg': "The training of your shift has encountered and error"}

            return {'msg': f"The status is {status}"}

        except AttributeError as e:
            return {'msg': "There are currently no jobs with the given ID"}
        except mongoengine.DoesNotExist:
            return {'msg': "The worker you are trying to get the status of has been deleted"}
