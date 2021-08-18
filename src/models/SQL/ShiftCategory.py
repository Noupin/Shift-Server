#pylint: disable=C0103, C0301
"""
The SQLAlchemy data model for a Shifts Category
"""
__author__ = "Noupin"

#Third Party Imports
from sqlalchemy.dialects.postgresql import UUID

#First Party Imports
from src import db
from src.models.SQL.Shift import Shift
from src.models.SQL.Category import Category


class ShiftCategory(db.Model):
    __tablename__ = 'shiftcategory'
    
    id = db.Column(db.Integer, primary_key=True)
    shift_id = db.Column(UUID(as_uuid=True), db.ForeignKey('shift.uuid'))
    category_name = db.Column(db.String, db.ForeignKey('category.name'))

    shift = db.relationship('Shift', backref='shiftCategories')
    category = db.relationship('Category', backref='shiftCategories')


    def __repr__(self) -> str:
        return f"ShiftCategory(name='{self.category_name}')"


    def __str__(self) -> str:
        return f"ShiftCategory(name='{self.category_name}')"
