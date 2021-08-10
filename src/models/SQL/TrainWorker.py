#pylint: disable=C0103, C0301
"""
The SQLAlchemy data model for a Train Worker
"""
__author__ = "Noupin"

#Third Party Imports
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID

#First Party Imports
from src import db


class TrainWorker(db.Model):
    """
    The Database data model for the Train celery worker.

    Args:
        shiftUUID (UUID, required): The UUID of the shift this worker is associated with.
        workerID (str): The id of the celery worker this database worker is associated with.
        timeStarted (datetime.datetime): The time the worker was created.
        training (bool): Whether or not the worker is training or not.
        inferencing (bool): Whether or not the worker is inferencing or not.
        imagesUpdated (bool): Whether or not the exhibit images are updated and ready to be sent to the front-end.
        exhibitImages (list of str): The binary encoded images to be sent to the frontend.
    """

    id = db.Column(db.Integer, primary_key=True)
    shiftUUID = db.Column(UUID(as_uuid=True), nullable=False)
    workerID = db.Column(db.String(40), nullable=False, unique=True, default='')
    timeStarted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    training = db.Column(db.Boolean, nullable=False, default=False)
    inferencing = db.Column(db.Boolean, nullable=False, default=False)
    imagesUpdated = db.Column(db.Boolean, nullable=False, default=False)
    _exhibitImages = db.Column(db.String, nullable=False, unique=True, default='')


    @property
    def exhibitImages(self):
        return [base64Image for base64Image in self._exhibitImages.split(';')]


    @exhibitImages.setter
    def exhibitImages(self, value):
        self._exhibitImages += f";{value}"


    def __repr__(self) -> str:
        return f"TrainWorker('shiftUUID={self.shiftUUID}, workerID={self.workerID}, training={self.training}, inferencing={self.inferencing}')"
    
    def __str__(self) -> str:
        return f"TrainWorker('shiftUUID={self.shiftUUID}, workerID={self.workerID}, training={self.training}, inferencing={self.inferencing}')"
