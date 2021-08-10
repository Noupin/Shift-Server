#pylint: disable=C0103, C0301
"""
The SQLAlchemy data model for a Shift
"""
__author__ = "Noupin"

#Third Party Imports
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID

#First Party Imports
from src import db
from src.constants import MAXIMUM_FILENAME_LENGTH, MAXIMUM_SHIFT_TITLE_LENGTH


class Shift(db.Model):
    __tablename__ = 'shift'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(MAXIMUM_SHIFT_TITLE_LENGTH), unique=True, nullable=False)
    dateCreated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    mediaFilename = db.Column(db.String(MAXIMUM_FILENAME_LENGTH), nullable=False, default='default.jpg')
    baseMediaFilename = db.Column(db.String(MAXIMUM_FILENAME_LENGTH), nullable=False, default='default.jpg')
    maskMediaFilename = db.Column(db.String(MAXIMUM_FILENAME_LENGTH), nullable=False, default='default.jpg')
    private = db.Column(db.Boolean, nullable=False, default=False)
    views = db.Column(db.Integer, nullable=False, default=0)
    verified = db.Column(db.Boolean, nullable=False, default=False)
    
    categories = db.relationship('Category', secondary='shiftcategory')


    def __repr__(self) -> str:
        return f"Shift(title='{self.title}', dateCreated='{self.dateCreated}', mediaFilename='{self.mediaFilename}')"
    
    
    def __str__(self) -> str:
        return f"Shift(title='{self.title}', dateCreated='{self.dateCreated}', mediaFilename='{self.mediaFilename}')"
