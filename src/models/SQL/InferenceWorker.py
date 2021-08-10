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
from src.constants import MAXIMUM_FILENAME_LENGTH


class InferenceWorker(db.Model):
    """
    The SQLAlchemy data model for the Inference celery worker.

    Args:
        shiftUUID (UUID, required): The UUID of the shift this worker is associated with.
        workerID (str): The id of the celery worker this Database worker is associated with.
        timeStarted (datetime.datetime): The time the worker was created.
        mediaFilename (str): The filename for the shifted media.
    """

    id = db.Column(db.Integer, primary_key=True)
    shiftUUID = db.Column(UUID(as_uuid=True), nullable=False)
    workerID = db.Column(db.String(40), nullable=False, unique=True, default='')
    timeStarted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    mediaFilename = db.Column(db.String(MAXIMUM_FILENAME_LENGTH), nullable=False, default='')
    baseMediaFilename = db.Column(db.String(MAXIMUM_FILENAME_LENGTH), nullable=False, default='')


    def __repr__(self) -> str:
        return f"InferenceWorker('{self.shiftUUID}, {self.datePosted}')"

    def __str__(self) -> str:
        return f"InferenceWorker('{self.shiftUUID}, {self.datePosted}')"
