#pylint: disable=C0103, C0301
"""
The SQLAlchemy data model for a Shift User
"""

from __future__ import annotations

__author__ = "Noupin"

#First Party Imports
from src import db


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    verified = db.Column(db.Boolean, nullable=False, default=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    canTrain = db.Column(db.Boolean, nullable=False, default=False)
    
    shifts = db.relationship('Shift', backref='author', lazy=True)


    def __repr__(self) -> str:
        return f"User(verified='{self.verified}', admin='{self.admin}', canTrain='{self.canTrain}')"


    def __str__(self) -> str:
        return f"User(verified='{self.verified}', admin='{self.admin}', canTrain='{self.canTrain}')"
