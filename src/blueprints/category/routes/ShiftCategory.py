#pylint: disable=C0103, C0301
"""
Shift Category endpoint for the Users part of the Shift API
"""
__author__ = "Noupin"

#Third Party Imports
from typing import List
from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs

#First Party Imports
from src.models.SQL.Shift import Shift
from src.constants import ITEMS_PER_PAGE
from src.models.Marshmallow.Shift import ShiftSchema
from src.models.SQL.ShiftCategory import ShiftCategory as ShiftCategoryModel
from src.models.Request.ShiftCategoryRequest import (ShiftCategoryRequest,
                                                         ShiftCategoryRequestDescription)
from src.models.Response.ShiftCategoryResponse import (ShiftCategoryResponse,
                                                           ShiftCategoryResponseDescription)


class ShiftCategory(MethodResource, Resource):

    @use_kwargs(ShiftCategoryRequest.Schema(), location="query",
                description=ShiftCategoryRequestDescription)
    @marshal_with(ShiftCategoryResponse,
                  description=ShiftCategoryResponseDescription)
    @doc(description="""The shifts for the queried category to display on the \
home page.""", tags=["Category"], operationId="Category")
    def get(self, queryParams: ShiftCategoryRequest, categoryName: str) -> dict:
        shiftCategories: List[ShiftCategoryModel] = ShiftCategoryModel.query.filter_by(name=categoryName).all()
        categoryShifts = []

        if not shiftCategories:
            return ShiftCategoryResponse().load(dict(shifts=categoryShifts))

        for shiftCategory in shiftCategories:
            shift = Shift.query.filter_by(uuid=shiftCategory.shift_id).first()
            categoryShifts.append(ShiftSchema().dump(shift))

        return ShiftCategoryResponse().load(dict(shifts=categoryShifts))
