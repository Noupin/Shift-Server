#pylint: disable=C0103, C0301
"""
The Categories Response Data Model for the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from marshmallow import fields, Schema


class CategoriesResponse(Schema):
    categories = fields.List(fields.String(), required=True)

categoriesResponseDescription = """The category names for the requested \
amount of categories."""
