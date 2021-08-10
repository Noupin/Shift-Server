#pylint: disable=C0103, C0301
"""
The SQLAlchemy data model for a Shifts Category
"""
__author__ = "Noupin"

#First Party Imports
from src import db
from src.constants import MAXIMUM_SHIFT_CATEGORY_TITLE_LENGTH


class Category(db.Model):
    __tablename__ = 'category'

    name = db.Column(db.String(MAXIMUM_SHIFT_CATEGORY_TITLE_LENGTH), unique=True, nullable=False, primary_key=True)
    shifts = db.relationship('Shift', secondary='shiftcategory')


    def __repr__(self) -> str:
        return f"CategoryName(name='{self.name}')"


    def __str__(self) -> str:
        return f"CategoryName(name='{self.name}')"
